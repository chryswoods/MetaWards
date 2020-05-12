#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
cimport openmp

from libc.math cimport sqrt, sin, cos, atan2, M_PI

import math

from .._parameters import Parameters
from .._network import Network

from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["add_wards_network_distance"]


cdef inline double deg_to_rad(double x) nogil:
    """Convert the passed angle in degrees to radians"""
    return x * M_PI / 180


cdef double distance_lat_long(double lon1, double lat1,
                              double lon2, double lat2) nogil:
    """Calculate the distance in kilometers between two lat/lon points on the
       Earth's surface
    """
    cdef double radius = 6378.16  # Earth's radius in km
    cdef double dlon = deg_to_rad(lon2 - lon1)
    cdef double dlat = deg_to_rad(lat2 - lat1)

    # Calculate using the haversin formula
    cdef double sin_dlat_over_2 = sin(dlat / 2.0)
    cdef double sin_dlon_over_2 = sin(dlon / 2.0)

    cdef double a = (sin_dlat_over_2 * sin_dlat_over_2) + \
                    (cos(deg_to_rad(lat1)) * cos(deg_to_rad(lat2)) *
                     sin_dlon_over_2 * sin_dlon_over_2)

    cdef double angle = 2.0 * atan2(sqrt(a), sqrt(1 - a))

    return angle * radius


cdef double distance_x_y(double x1, double y1,
                         double x2, double y2) nogil:
    """Calculate the distance between two x/y points on
       a plane, in the units of the points (hopefully they
       are in kilometers too...)
    """
    cdef double dx = x1 - x2
    cdef double dy = y1 - y2

    dx *= dx
    dy *= dy

    return sqrt(dx + dy)


def add_wards_network_distance(network: Network, nthreads: int = 1):
    """Reads the location data in network.parameters.input_files.position
       and adds those locations to all of the nodes in the passed
       network. Then it calculates all of the distances between
       the nodes for each link and puts that into the
       'distance' property of each link
    """

    # ncov build does not have WEEKEND defined, so not writing this code now
    params = network.params
    wards = network.nodes
    links = network.links
    play = network.play

    line = None

    print("Reading in the positions...")

    cdef int i1 = 0
    cdef double x = 0.0
    cdef double y = 0.0

    cdef double * wards_x = get_double_array_ptr(wards.x)
    cdef double * wards_y = get_double_array_ptr(wards.y)

    cdef scale_for_km = 1.0

    if params.input_files.coordinates == "x/y":
        calc_distance = distance_x_y
        scale_for_km = 0.001
    elif params.input_files.coordinates == "lat/long":
        calc_distance = distance_lat_long
        scale_for_km = 1.0
    else:
        raise ValueError(f"Unrecognised coordinate system "
                         f"{params.input_files.coordinates}")

    try:
        with open(params.input_files.position, "r") as FILE:
            line = FILE.readline()

            while line:
                words = line.split()
                i1 = int(words[0])
                x = float(words[1])
                y = float(words[2])

                wards.x[i1] = x * scale_for_km
                wards.y[i1] = y * scale_for_km

                if (x == 0) and (y == 0):
                    print(f"WARNING: Position of ward {i1} is 0,0. This "
                          f"doesn't seem right")

                line = FILE.readline()
    except Exception as e:
        raise ValueError(f"{params.input_files.position} is corrupted or "
                         f"unreadable? Error = {e.__class__}: {e}, "
                         f"line = {line}")

    # make sure that all nodes have valid distances
    cdef int i = 0
    cdef int nmissing = 0

    for i in range(1, network.nnodes+1):
        x = wards.x[i]
        y = wards.y[i]

        if (x == 0) and (y == 0):
            nmissing += 1
            if nmissing == 20:
                print("Not printing any more missing positions as there "
                      "are too many. You should fix the positions file")
            elif nmissing < 20:
                print(f"WARNING: Position of ward {i} does not appear to have "
                      f"been set - position is ({x} {y}).")

    if nmissing > 0:
        print(f"In total the number of wards with missing positions "
              f"is {nmissing}")

    print("Calculating distances...")

    cdef double total_distance = 0
    cdef double distance, distance2

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)

    cdef int * play_ifrom = get_int_array_ptr(play.ifrom)
    cdef int * play_ito = get_int_array_ptr(play.ito)

    cdef double * links_distance = get_double_array_ptr(links.distance)
    cdef double * play_distance = get_double_array_ptr(play.distance)

    cdef double x1 = 0.0
    cdef double x2 = 0.0
    cdef double y1 = 0.0
    cdef double y2 = 0.0

    cdef int nlinks_plus_one = network.nlinks + 1
    cdef int nplay_plus_one = network.nplay + 1

    cdef double too_large = 1000000 * scale_for_km

    cdef int ifrom = 0
    cdef int ito = 0

    cdef int num_threads = nthreads

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nlinks_plus_one, schedule="static"):
            ifrom = links_ifrom[i]
            ito = links_ito[i]

            x1 = wards_x[ifrom]
            y1 = wards_y[ifrom]

            x2 = wards_x[ito]
            y2 = wards_y[ito]

            if (x1 == 0 and y1 == 0) or (x2 == 0 and y2 == 0):
                links_distance[i] = 0.0
            else:
                # skipping null points
                distance = calc_distance(x1, y1, x2, y2)

                links_distance[i] = distance
                total_distance += distance

                if distance > too_large:
                    with gil:
                        print(f"Large distance between wards {ifrom} "
                              f"and {ito}: {distance} km? {x1},{y1}  "
                              f"{x2},{y2}")

    print(f"Total links distance equals {total_distance}")

    cdef double total_play_distance = 0.0

    if network.nplay > 0:
        with nogil, parallel(num_threads=1):
            for i in prange(1, nplay_plus_one, schedule="static"):
                ifrom = play_ifrom[i]
                ito = play_ito[i]

                x1 = wards_x[ifrom]
                y1 = wards_y[ifrom]

                x2 = wards_x[ito]
                y2 = wards_y[ito]

                if (x1 == 0 and y1 == 0) or (x2 == 0 and y2 == 0):
                    play_distance[i] = 0.0
                else:
                    # skipping null points
                    distance = calc_distance(x1, y1, x2, y2)

                    play_distance[i] = distance
                    total_play_distance += distance

                    if distance > too_large:
                        with gil:
                            print(f"Large distance between play wards {ifrom} "
                                  f"and {ito}: {distance} km? {x1},{y1}  "
                                  f"{x2},{y2}")

    print(f"Total play distance equals {total_play_distance}")
    print(f"Total distance equals {total_distance+total_play_distance}")

    return network
