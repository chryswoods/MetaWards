
from metawards import Population, Populations

import pickle


def test_populations():
    traj = Populations()

    pop = Population(initial=100, susceptibles=95, latent=0,
                     total=0, recovereds=0)

    assert pop.initial == 100
    assert pop.susceptibles == 95
    assert pop.latent == 0
    assert pop.total == 0
    assert pop.recovereds == 0
    assert pop.population == 95 + 0 + 0

    traj.append(pop)

    assert traj[0] == pop

    pop.susceptibles -= 10
    pop.latent += 5
    pop.total += 4
    pop.recovereds += 1

    assert traj[0].initial == 100
    assert traj[0].susceptibles == 95
    assert traj[0].latent == 0
    assert traj[0].total == 0
    assert traj[0].recovereds == 0
    assert traj[0].population == 95 + 0 + 0

    traj.append(pop)

    assert traj[1].initial == 100
    assert traj[1].susceptibles == 85
    assert traj[1].latent == 5
    assert traj[1].total == 4
    assert traj[1].recovereds == 1
    assert traj[1].population == 85 + 5 + 4 + 1

    pop.susceptibles -= 20
    pop.latent += 3
    pop.total += 14
    pop.recovereds += 3

    traj.append(pop)

    assert traj[2].initial == 100
    assert traj[2].susceptibles == 65
    assert traj[2].latent == 8
    assert traj[2].total == 18
    assert traj[2].recovereds == 4
    assert traj[2].population == 65 + 8 + 18 + 4

    s = pickle.dumps(traj)

    traj2 = pickle.loads(s)

    assert traj == traj2


if __name__ == "__main__":
    test_populations()
