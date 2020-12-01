
from metawards import Network, Ward, Parameters, Disease, Population, \
    OutputFiles, PersonType
from metawards.movers import go_ward, go_record, MoveGenerator, MoveRecord

import os

script_dir = os.path.dirname(__file__)


def move_bristol(**kwargs):
    record = MoveRecord()

    def go_bristol(**kwargs):
        gen = MoveGenerator(from_ward=["bristol", "london"],
                            to_ward="oxford")
        go_ward(generator=gen, record=record, **kwargs)

        # at least 2 moves - from Bristol and London
        assert len(record) >= 2

        for m in record:
            (from_demo, from_stage, from_type, from_ward,
             to_demo, to_stage, to_type, to_ward, number) = m

            assert from_demo == 0
            assert to_demo == 0
            assert from_stage == to_stage
            assert from_type == to_type
            assert to_ward == 3
            assert from_ward in [1, 2]
            assert number > 0
            assert number <= 100

    def go_invert(**kwargs):
        # immediately return individuals from whence they came
        invert = record.invert()
        record2 = MoveRecord()
        go_record(moves=invert, record=record2, **kwargs)

        invert2 = record2.invert()

        for m1, m2 in zip(record, invert2):
            assert m1 == m2

    return [go_bristol, go_invert]


def test_go_record():
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
                                        mover=move_bristol)

    OutputFiles.remove(outdir, prompt=None)

    # despite the moves, only Bristolians can be infected as there
    # are no work movements
    assert trajectory[-1].recovereds <= 100


if __name__ == "__main__":
    test_go_record()
