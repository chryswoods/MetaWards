
from libc.math cimport sqrt

from .._network import Network
from .._infections import Infections
from .._parameters import Parameters
from ._profiler import Profiler, NullProfiler
from .._population import Population
from ._workspace import Workspace

__all__ = ["extract_data_for_graphics"]


def extract_data_for_graphics(network: Network, infections: Infections,
                              workspace: Workspace,
                              FILE, profiler: Profiler = None):
    """Extract data that will be used for graphical analysis"""
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("extract_data_for_graphics")

    links = network.to_links

    cdef int N_INF_CLASSES = len(infections)

    assert workspace.N_INF_CLASSES == N_INF_CLASSES
    assert workspace.MAXSIZE >= network.nnodes+1

    play_infections = infections.play
    infections = infections.work

    workspace.zero_all()

    cdef int i, j, inf_ij, pinf_ij, ifrom
    cdef int total = 0

    cdef int [::1] infections_i, play_infections_i
    cdef int [::1] inf_tot = workspace.inf_tot
    cdef int [::1] total_inf_ward = workspace.total_inf_ward
    cdef int [::1] total_infections = workspace.total_infections
    cdef int [::1] prevalence = workspace.prevalence
    cdef int [::1] links_ifrom = links.ifrom

    p = p.start("loop_over_n_inf_classes")

    for i in range(0, N_INF_CLASSES):
        infections_i = infections[i]
        play_infections_i = play_infections[i]

        for j in range(1, network.nnodes+1):
            total_inf_ward[j] = 0

        for j in range(1, network.nlinks+1):
            inf_ij = infections_i[j]
            if inf_ij != 0:
                inf_tot[i] += inf_ij
                ifrom = links_ifrom[j]
                total_inf_ward[ifrom] += inf_ij
                if i < N_INF_CLASSES-1:
                    total_infections[ifrom] += inf_ij
                    total += inf_ij

        for j in range(1, network.nnodes+1):
            pinf_ij = play_infections_i[j]
            total_inf_ward[j] += pinf_ij
            if (pinf_ij != 0) and (i < N_INF_CLASSES-1):
                total_infections[j] += pinf_ij
                total += pinf_ij

            if i == 2:
                FILE.write("%d " % total_infections[j])   # incidence

            if i == N_INF_CLASSES - 1:
                FILE.write("%d ", total_infections[j])  # prevalence

            if i == N_INF_CLASSES - 1:
                prevalence[j] = total_infections[j]

    FILE.write("\n")

    p = p.stop()
    p.stop()

    return total
