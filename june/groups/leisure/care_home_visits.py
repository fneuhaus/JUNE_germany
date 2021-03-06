import numpy as np
import pandas as pd
import yaml
from random import randint, choice
from june.geography import Areas, SuperAreas
from june.groups import CareHomes, Households, Household, CareHome

from .social_venue import SocialVenue, SocialVenues, SocialVenueError
from .social_venue_distributor import SocialVenueDistributor
from june.paths import data_path, configs_path

default_config_filename = configs_path / "defaults/groups/leisure/care_home_visits.yaml"


class CareHomeVisitsDistributor(SocialVenueDistributor):
    def __init__(
        self,
        poisson_parameters: dict = None,
        neighbours_to_consider=None,
        maximum_distance=None,
        weekend_boost: float = 2.0,
        drags_household_probability=1.0,
    ):
        super().__init__(
            social_venues=None,
            poisson_parameters=poisson_parameters,
            neighbours_to_consider=neighbours_to_consider,
            maximum_distance=maximum_distance,
            weekend_boost=weekend_boost,
            drags_household_probability=drags_household_probability,
        )

    @classmethod
    def from_config(cls, config_filename: str = default_config_filename):
        with open(config_filename) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return cls(**config)

    def link_households_to_care_homes(self, super_areas):
        """
        Links households and care homes in the giving super areas. For each care home,
        we find a random house in the super area and link it to it.
        The house needs to be occupied by a family, or a couple.

        Parameters
        ----------
        super_areas
            list of super areas
        """
        for super_area in super_areas:
            households_super_area = []
            for area in super_area.areas:
                households_super_area += [
                    household
                    for household in area.households
                    if household.type in ["family", "ya_parents", "nokids"]
                ]
            for area in super_area.areas:
                if area.care_home is not None:
                    for person in area.care_home.residents:
                        for i in range(5):
                            household = choice(households_super_area)
                            if len(household.residences_to_visit.get("care_home", [])) < 2:
                                break
                        household.residences_to_visit["care_home"] = (
                            *household.residences_to_visit.get("care_home", []),
                            area.care_home
                        )

    def get_social_venue_for_person(self, person):
        care_homes_to_visit = person.residence.group.residences_to_visit["care_home"]
        if care_homes_to_visit is None:
            return None
        return care_homes_to_visit[randint(0, len(care_homes_to_visit) - 1)]

    def get_leisure_subgroup_type(self, person):
        return CareHome.SubgroupType.visitors
