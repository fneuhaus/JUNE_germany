import copy
import datetime
import re
import sys
import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Optional, List, Dict

import yaml

from june import paths
from june.demography.person import Person
from june.groups.leisure import Leisure
from june.infection.symptom_tag import SymptomTag
from june.groups.leisure.social_venue_distributor import parse_age_probabilites
from june.interaction import Interaction

# TODO: reduce leisure attendance

default_config_filename = paths.configs_path / "defaults/policy/policy.yaml"


class PolicyError(BaseException):
    pass


class Policy(ABC):
    def __init__(
        self,
        start_time: Union[str, datetime.datetime] = "1900-01-01",
        end_time: Union[str, datetime.datetime] = "2100-01-01",
    ):
        """
        Template for a general policy.

        Parameters
        ----------
        start_time:
            date at which to start applying the policy
        end_time:
            date from which the policy won't apply
        """
        self.spec = self.get_spec()
        self.start_time = self.read_date(start_time)
        self.end_time = self.read_date(end_time)

    @staticmethod
    def read_date(date: Union[str, datetime.datetime]) -> datetime.datetime:
        """
        Read date in two possible formats, either string or datetime.date, both
        are translated into datetime.datetime to be used by the simulator

        Parameters
        ----------
        date:
            date to translate into datetime.datetime

        Returns
        -------
            date in datetime format
        """
        if type(date) is str:
            return datetime.datetime.strptime(date, "%Y-%m-%d")
        elif isinstance(date, datetime.date):
            return datetime.datetime.combine(date, datetime.datetime.min.time())
        else:
            raise TypeError("date must be a string or a datetime.date object")

    def get_spec(self) -> str:
        """
        Returns the speciailization of the policy.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).lower()

    def is_active(self, date: datetime.datetime) -> bool:
        """
        Returns true if the policy is active, false otherwise

        Parameters
        ----------
        date:
            date to check
        """
        return self.start_time <= date < self.end_time


class SocialDistancing(Policy):
    def __init__(
        self,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        beta_factors: dict = None,
    ):
        super().__init__(start_time, end_time)
        self.original_betas = {}
        self.beta_factors = beta_factors
        for key in beta_factors.keys():
            self.original_betas[key] = None  # to be filled when coupled to interaction


class SkipActivity(Policy):
    """
    Template for policies that will ban an activity for a person
    """

    @abstractmethod
    def skip_activity(self, person: "Person", activities: List[str],) -> bool:
        """
        Returns True if the activity is to be skipped, otherwise False
        """
        pass

    def remove_activities(
        self, activities: List[str], activities_to_remove: List[str]
    ) -> List[str]:
        """
        Remove an activity from a list of activities

        Parameters
        ----------
        activities:
            list of activities
        activity_to_remove:
            activity that will be removed from the list
        """
        return [
            activity for activity in activities if activity not in activities_to_remove
        ]


class StayHome(Policy):
    """
    Template for policies that will force someone to stay at home
    """

    @abstractmethod
    def must_stay_at_home(self, person: "Person", days_from_start: float):
        """
        Returns True if Person must stay at home, otherwise False

        Parameters
        ----------
        person: 
            person to whom the policy is being applied

        days_from_start:
            time past from beginning of simulation, in units of days
        """
        pass


class CloseLeisureVenue(Policy):
    def __init__(
        self,
        start_time: Union[str, datetime.datetime] = "1900-01-01",
        end_time: Union[str, datetime.datetime] = "2100-01-01",
        venues_to_close=("cinemas", "groceries"),
    ):
        """
        Template for policies that will close types of leisure venues

        Parameters
        ----------
        start_time:
            date at which to start applying the policy
        end_time:
            date from which the policy won't apply
        venues_to_close:
            list of leisure venues that will close
        """

        super().__init__(start_time, end_time)
        self.venues_to_close = venues_to_close


class PermanentPolicy(StayHome):
    def must_stay_at_home(self, person: "Person", days_from_start: float) -> bool:
        """
        Returns True if person has symptoms, otherwise False

        Parameters
        ----------
        person: 
            person to whom the policy is being applied

        days_from_start:
            time past from beginning of simulation, in units of days
        """
        return (
            person.health_information is not None
            and person.health_information.tag is SymptomTag.severe
        )


class Quarantine(StayHome):
    def __init__(
        self,
        start_time: Union[str, datetime.datetime] = "1900-01-01",
        end_time: Union[str, datetime.datetime] = "2100-01-01",
        n_days: int = 7,
        n_days_household: int = 14,
        household_complacency: float = 1.0,
    ):
        """
        This policy forces people to stay at home for ```n_days``` days after they show symtpoms, and for ```n_days_household``` if someone else in their household shows symptoms

        Parameters
        ----------
        start_time:
            date at which to start applying the policy
        end_time:
            date from which the policy won't apply
        n_days:
            days for which the person has to stay at home if they show symtpoms
        n_days_household:
            days for which the person has to stay at home if someone in their household shows symptoms
        household_complacency:
            percentage of people that will adhere to the hoseuhold quarantine policy
        """
        super().__init__(start_time, end_time)
        self.n_days = n_days
        self.n_days_household = n_days_household
        self.household_complacency = household_complacency

    def must_stay_at_home(self, person: "Person", days_from_start):
        self_quarantine = False
        try:
            if person.symptoms.tag in (SymptomTag.mild, SymptomTag.severe):
                time_of_symptoms_onset = (
                    person.health_information.time_of_symptoms_onset
                )
                release_day = time_of_symptoms_onset + self.n_days
                if release_day > days_from_start > time_of_symptoms_onset:
                    self_quarantine = True
            else:
                self_quarantine = False
        except:
            pass
        housemates_quarantine = person.residence.group.quarantine(
            days_from_start,
            self.n_days_household,
            household_complacency=self.household_complacency,
        )
        return self_quarantine or housemates_quarantine


class Shielding(StayHome):
    def __init__(
        self,
        start_time: str,
        end_time: str,
        min_age: int,
        complacency: Optional[float] = None,
    ):
        super().__init__(start_time, end_time)
        self.min_age = min_age
        self.complacency = complacency

    def must_stay_at_home(self, person: "Person", days_from_start: float):
        if person.age >= self.min_age:
            if self.complacency is None or np.random.rand() < self.complacency:
                return True
        return False


class CloseSchools(SkipActivity):
    def __init__(
        self, start_time: str, end_time: str, years_to_close=None, full_closure=None,
    ):
        super().__init__(start_time, end_time)
        self.full_closure = full_closure
        self.years_to_close = years_to_close
        if self.years_to_close == "all":
            self.years_to_close = np.arange(0, 20)

    def _check_kid_goes_to_school(self, person: "Person"):
        """
        Checks if a kid should go to school when there is a lockdown.
        The rule is that a kid goes to school if the age is below 14 (not included)
        and there are at least two key workers at home.
        """
        if person.age < 14:
            keyworkers_parents = 0
            for person in person.residence.group.residents:
                if person.lockdown_status == "key_worker":
                    keyworkers_parents += 1
                    if keyworkers_parents > 1:
                        return True
        return False

    def skip_activity(
        self, person: "Person", activities: List,
    ):
        if (
            person.primary_activity is not None
            and person.primary_activity.group.spec == "school"
        ):
            if (
                self.full_closure or person.age in self.years_to_close
            ) and not self._check_kid_goes_to_school(person):
                return self.remove_activities(activities, ["primary_activity"])
        return activities


class CloseUniversities(SkipActivity):
    def __init__(
        self, start_time: str, end_time: str,
    ):
        super().__init__(start_time, end_time)

    def skip_activity(
        self, person: "Person", activities: List,
    ):
        if (
            person.primary_activity is not None
            and person.primary_activity.group.spec == "university"
        ):
            return self.remove_activities(activities, ["primary_activity"])
        return activities


class CloseCompanies(SkipActivity):
    def __init__(
        self, start_time: str, end_time: str, full_closure=False, random_work_probability=None
    ):
        """
        Prevents workers with the tag ``person.lockdown_status=furlough" to go to work.
        If full_closure is True, then no one will go to work.
        """
        super().__init__(start_time, end_time)
        self.full_closure = full_closure
        self.random_work_probability =random_work_probability 

    def skip_activity(
        self, person: "Person", activities: List,
    ):
        if (
            person.primary_activity is not None
            and person.primary_activity.group.spec == "company"
        ):

            if self.full_closure or person.lockdown_status == "furlough":
                return self.remove_activities(
                    activities, ["primary_activity", "commute"]
                )
            elif person.lockdown_status == "random" and self.random_work_probability is not None:
                if np.random.rand() > self.random_work_probability:
                    return self.remove_activities(
                        activities, ["primary_activity", "commute"]
                    )
        return activities


class ChangeLeisureProbability(Policy):
    def __init__(
        self,
        start_time: str,
        end_time: str,
        leisure_activities_probabilities: Dict[str, Dict[str, Dict[str, float]]],
    ):
        """
        Changes the probability of the specified leisure activities.

        Parameters
        ----------
        - start_time : starting time of the policy.
        - end_time : end time of the policy.
        - leisure_activities_probabilities : dictionary where the first key is an age range, and the second  a
            number with the new probability for the activity in that age. Example:
            * leisure_activities_probabilities = {"pubs" : {"men" :{"0-50" : 0.5, "50-99" : 0.2}, "women" : {"0-70" : 0.2, "71-99" : 0.8}}}
        """
        super().__init__(start_time, end_time)
        self.leisure_probabilities = {}
        self.original_leisure_probabilities = {}
        for activity in leisure_activities_probabilities:
            self.leisure_probabilities[activity] = {}
            self.leisure_probabilities[activity]["men"] = parse_age_probabilites(
                leisure_activities_probabilities[activity]["men"]
            )
            self.leisure_probabilities[activity]["women"] = parse_age_probabilites(
                leisure_activities_probabilities[activity]["women"]
            )
            self.original_leisure_probabilities[
                activity
            ] = {}  # this will be filled when coupled to leisure

    def is_active(self, date: datetime.datetime) -> bool:
        """
        This is modified in this policy to include the end date.
        """
        return self.start_time <= date <= self.end_time

class PolicyCollection(ABC):
    def __init__(self, policies: List[Policy]):
        """
        A collection of like policies active on the same date
        """
        self.policies = policies


class SkipActivityCollection(PolicyCollection):
    policies: List[SkipActivity]

    def __call__(
        self, person: Person, activities: List,
    ):
        """
        Filter activities this person is not permitted to do on a given date

        Parameters
        ----------
        person
            A person who has been a very naughty boy
        activities
            Things they are not currently permitted to do

        Returns
        -------
        Activities the person may still do
        """
        for policy in self.policies:
            activities = policy.skip_activity(person, activities)
        return activities


class StayHomeCollection(PolicyCollection):
    policies: List[StayHome]

    def __call__(self, person: Person, days_from_start: int):
        """
        Must a person stay at home a given number of days from some event

        Parameters
        ----------
        person
            A person
        days_from_start
            The number of days that have passed

        Returns
        -------
        True if the person has to stay home
        """
        if person.hospital is None:
            for policy in self.policies:
                if policy.must_stay_at_home(person, days_from_start):
                    return True
        return False


class Policies:
    def __init__(self, policies=None):
        self.policies = [PermanentPolicy()] + (policies or list())

    @classmethod
    def from_file(
        cls, config_file=default_config_filename,
    ):
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        policies = []
        for policy, policy_data in config.items():
            camel_case_key = "".join(
                x.capitalize() or "_" for x in policy.split("_")
            )
            if "start_time" not in policy_data:
                for policy_i, policy_data_i in policy_data.items():
                    if (
                        "start_time" not in policy_data_i.keys()
                        or "end_time" not in policy_data_i.keys()
                    ):
                        raise ValueError("policy config file not valid.")
                    policies.append(str_to_class(camel_case_key)(**policy_data_i))
            else:
                policies.append(str_to_class(camel_case_key)(**policy_data))
        return Policies(policies=policies)

    def get_active_policies_for_type(self, policy_type, date):
        return [
            policy
            for policy in self.policies
            if isinstance(policy, policy_type) and policy.is_active(date)
        ]

    def _stay_home_policies(self, date):
        return self.get_active_policies_for_type(policy_type=StayHome, date=date)

    def _skip_activity_policies(self, date):
        return self.get_active_policies_for_type(policy_type=SkipActivity, date=date)

    def skip_activity_collection(self, *, date) -> SkipActivityCollection:
        """
        Collection of SkipActivity policies in force on the given date
        """
        return SkipActivityCollection(self._skip_activity_policies(date))

    def stay_home_collection(self, *, date) -> StayHomeCollection:
        """
        Collection of StayHome policies in force on the given date
        """
        return StayHomeCollection(self._stay_home_policies(date))

    def get_social_distancing_policies(self, date):
        return self.get_active_policies_for_type(
            policy_type=SocialDistancing, date=date
        )

    def close_venues_policies(self, date):
        return self.get_active_policies_for_type(
            policy_type=CloseLeisureVenue, date=date
        )

    def get_change_leisure_probabilities_policies(self, date):
        return self.get_active_policies_for_type(
            policy_type=ChangeLeisureProbability, date=date
        )

    def apply_social_distancing_policy(self, date, interaction: Interaction):
        """
        Implement social distancing policy
        
        -----------
        Parameters:
        betas: e.g. (dict) from DefaultInteraction, e.g. DefaultInteraction.from_file(selector=selector).beta

        Assumptions:
        - Currently we assume that social distancing is implemented first and this affects all
          interactions and intensities globally
        - Currently we assume that the changes are not group dependent
        TODO:
        - Implement structure for people to adhere to social distancing with a certain compliance
        - Check per group in config file
        """
        social_distancing_policies = self.get_social_distancing_policies(date)
        # order matters, first deactivate all policies that expire in this day.
        for policy in social_distancing_policies:
            if policy.end_time == date:  # deactivate policy, restore betas.
                for key, value in policy.original_betas.items():
                    interaction.beta[key] = value

        # now activate all policies that need to be activated
        for policy in social_distancing_policies:
            if policy.start_time == date:  # activate policy, save current betas.
                for key, value in policy.beta_factors.items():
                    policy.original_betas[key] = interaction.beta[key]
                    interaction.beta[key] = interaction.beta[key] * value

    def get_beta_factors(self, group):
        pass

    def find_closed_venues(self, date):
        closed_venues = set()
        for policy in self.close_venues_policies(date):
            closed_venues.update(policy.venues_to_close)
        return closed_venues

    def apply_change_probabilities_leisure(self, date, leisure: Leisure):
        """
        Changes probabilities of doing leisure activities according to the policies specified.
        The current probabilities are stored in the policies, and restored at the end of the policy 
        time span. Keep this in mind when trying to stack policies that modify the same social venue.
        """
        active_policies = self.get_change_leisure_probabilities_policies(date)
        for policy in active_policies:
            if policy.start_time == date:
                # activate policy
                for activity in policy.leisure_probabilities:
                    if activity not in leisure.leisure_distributors:
                        raise PolicyError(
                            "Trying to change leisure probability for a non-existing activity"
                        )
                    activity_distributor = leisure.leisure_distributors[activity]
                    policy.original_leisure_probabilities[activity][
                        "men"
                    ] = activity_distributor.male_probabilities
                    policy.original_leisure_probabilities[activity][
                        "women"
                    ] = activity_distributor.female_probabilities
                    activity_distributor.male_probabilities = policy.leisure_probabilities[
                        activity
                    ][
                        "men"
                    ]
                    activity_distributor.female_probabilities = policy.leisure_probabilities[
                        activity
                    ][
                        "women"
                    ]
            elif policy.end_time == date:
                # restore policy
                for activity in policy.leisure_probabilities:
                    if activity not in leisure.leisure_distributors:
                        raise PolicyError(
                            "Trying to restore a leisure probability for a non-existing activity"
                        )
                    activity_distributor = leisure.leisure_distributors[activity]
                    activity_distributor.male_probabilities = policy.original_leisure_probabilities[
                        activity
                    ][
                        "men"
                    ]
                    activity_distributor.female_probabilities = policy.original_leisure_probabilities[
                        activity
                    ][
                        "women"
                    ]


def str_to_class(classname):
    return getattr(sys.modules["june.policy"], classname)
