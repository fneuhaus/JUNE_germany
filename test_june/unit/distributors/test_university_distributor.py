from june.demography import Person
from june.distributors import UniversityDistributor
from june.groups import University, Universities
from june.geography import Geography
from june.world import generate_world_from_geography

import pytest


@pytest.fixture(name="world")
def create_world():
    geography = Geography.from_file(
        {"super_area": ["D07315", "D07339", "D07331",]}
    )
    world = generate_world_from_geography(geography, include_households=True)
    return world


def test__students_go_to_uni(world):
    universities = Universities.for_areas(world.areas)
    mainz = universities[0]
    university_distributor = UniversityDistributor(universities)
    university_distributor.distribute_students_to_universities(
        areas=world.areas, people=world.people
    )
    assert mainz.n_students > 10000
