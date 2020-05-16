"""
This is a quick test that makes sure the box model can be run. It does not check whether it is doing anything correctly,
but at least we can use it in the meantime to make sure the code runs before pusing it to master.
"""

import os

from june.seed import Seed


def test_box_full_run(simulator_box):

    seed = Seed(simulator_box.world.boxes, simulator_box.infection, )
    seed.unleash_virus(1000, box_mode=True)
    simulator_box.run()
    print(len(simulator_box.world.people))
    print(len(simulator_box.world.people.infected))
    simulator_box.logger.plot_infection_curves_per_day()
