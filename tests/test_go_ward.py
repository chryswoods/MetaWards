
from metawards import Network, Ward, Parameters, Disease, Population, \
    OutputFiles, PersonType
from metawards.movers import go_ward, MoveGenerator, MoveRecord

import os

script_dir = os.path.dirname(__file__)


def move_cycle(**kwargs):
    # move individuals back to S when they hit R
    def go_cycle(population, **kwargs):
        generator = MoveGenerator(from_stage="R", to_stage="S")

        old_recovereds = population.recovereds

        record = MoveRecord()
        go_ward(population=population, generator=generator,
                record=record, **kwargs)

        for r in record:
            (from_dem, from_stage, from_typ, from_ward,
             to_dem, to_stage, to_typ, to_ward, number) = r

            assert from_dem == 0
            assert to_dem == 0
            assert from_stage == 2
            assert to_stage == -1
            assert PersonType.PLAYER == from_typ
            assert PersonType.PLAYER == to_typ
            assert from_ward == to_ward
            assert number == old_recovereds

    return [go_cycle]


def move_bristol(**kwargs):

    # move everyone to Bristol
    def go_bristol(population, **kwargs):
        gen = MoveGenerator(to_ward="bristol")
        record = MoveRecord()
        go_ward(population=population, generator=gen, record=record, **kwargs)

        if population.day == 1:
            from array import array
            # this should have moved everyone to Bristol
            assert len(record) == 2
            # move all 100 players from london to bristol
            assert array("i", (0, -1, 2, 2, 0, -1, 2, 1, 100)) in record
            # move all 100 players from oxford to bristol
            assert array("i", (0, -1, 2, 3, 0, -1, 2, 1, 100)) in record
        else:
            # no-one left to move
            assert len(record) == 0

    return [go_bristol]


def move_travel(network, **kwargs):
    from metawards import WardID

    def go_travel1(**kwargs):
        gen = MoveGenerator(from_ward=[WardID("bristol", all_commute=True),
                                       WardID("bristol")],
                            from_stage="E",
                            to_ward="london",
                            to_stage="E",
                            fraction=0.5)
        record = MoveRecord()
        go_ward(generator=gen, record=record, **kwargs)

        for r in record:
            (from_dem, from_stage, from_typ, from_ward,
             to_dem, to_stage, to_typ, to_ward, number) = r
            print(r)

            assert from_dem == 0
            assert to_dem == 0
            assert from_stage == 0
            assert to_stage == 0
            assert from_ward == 1
            assert to_ward == 2
            assert number < 100

    def go_travel2(**kwargs):
        gen = MoveGenerator(from_ward=[WardID("bristol", all_commute=True),
                                       WardID("bristol")],
                            from_stage="E",
                            to_ward="oxford",
                            to_stage="E",
                            fraction=1.0)
        record = MoveRecord()
        go_ward(generator=gen, record=record, **kwargs)

        for r in record:
            (from_dem, from_stage, from_typ, from_ward,
             to_dem, to_stage, to_typ, to_ward, number) = r
            print(r)

            assert from_dem == 0
            assert to_dem == 0
            assert from_stage == 0
            assert to_stage == 0
            assert from_ward == 1
            assert to_ward == 3
            assert number < 100

    def go_travel3(**kwargs):
        gen = MoveGenerator(from_ward=[WardID("bristol", all_commute=True),
                                       "bristol",
                                       WardID("london", all_commute=True),
                                       "london"],
                            from_stage="R",
                            to_ward="oxford",
                            to_stage="R")
        record = MoveRecord()
        go_ward(generator=gen, record=record, **kwargs)

        for r in record:
            (from_dem, from_stage, from_typ, from_ward,
             to_dem, to_stage, to_typ, to_ward, number) = r

            print(r)
            assert from_dem == 0
            assert to_dem == 0
            assert from_stage == 2
            assert to_stage == 2
            assert from_ward in [1, 2]
            assert to_ward == 3

    return [go_travel1, go_travel2, go_travel3]


def test_go_ward():
    bristol = Ward("bristol")
    london = Ward("london")
    oxford = Ward("oxford")

    bristol.set_num_players(100)
    london.set_num_players(100)
    oxford.set_num_players(100)

    bristol.add_workers(0, destination=london)
    bristol.add_workers(0, destination=oxford)
    oxford.add_workers(0, destination=bristol)
    oxford.add_workers(0, destination=london)
    london.add_workers(0, destination=bristol)
    london.add_workers(0, destination=oxford)

    disease = Disease(name="lurgy")
    disease.add(name="E", beta=0.5, progress=0.5)
    disease.add(name="I", beta=0.8, progress=0.25)
    disease.add(name="R")
    disease.assert_sane()

    params = Parameters()
    params.set_disease(disease)
    params.add_seeds("1 20 bristol")

    outdir = os.path.join(script_dir, "test_go_ward_output")

    network = Network.from_wards(bristol + london + oxford, params=params)

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        nthreads=1)

    print(trajectory[-1])

    # there are no workers, so can only infect the 100 Bristolians
    assert trajectory[-1].recovereds <= 100

    # Repeat with a different number of threads to test parallel code
    outdir = os.path.join(script_dir, "test_go_ward_output")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        nthreads=4)

    print(trajectory[-1])

    # there are no workers, so can only infect the 100 Bristolians
    assert trajectory[-1].recovereds <= 100

    # now do a cyclic move, from "R" to "S"
    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        mover=move_cycle,
                                        nsteps=200)

    print(trajectory[-1])

    # we should have completed all 200 steps as this will never end
    assert trajectory[-1].day == 200
    assert trajectory[-1].recovereds <= 100

    # move everyone to Bristol
    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        mover=move_bristol)

    print(trajectory[-1])
    assert trajectory[-1].recovereds > 100

    # now move through all of bristol, london, oxford
    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        mover=move_travel)

    print(trajectory[-1])
    assert trajectory[-1].recovereds > 100

    OutputFiles.remove(outdir, prompt=None)


if __name__ == "__main__":
    test_go_ward()
