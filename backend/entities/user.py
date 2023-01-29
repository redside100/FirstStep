from dataclasses import dataclass
from consts import *
from entities.rating import Rating
from enum import Enum

class OnboardingStatus(Enum):
  NotStarted = 0 # have not started onboarding
  Step0 = 1 # tbd user's basic details
  Step1 = 2 # tbd user's skills
  Step2 = 3 # tbd user's preferences
  Completed = 4 # completd onboarding

@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    program: str
    avatar_url: str
    bio: str
    ratings: Rating
    group_id: int

    @staticmethod
    def from_database(db_entry, ratings):
        return User(db_entry['id'], db_entry['first_name'], db_entry['last_name'], str(db_entry['program_id']),
                    db_entry['avatar_url'], db_entry['bio'], ratings, db_entry['group_id'])


@dataclass
class UserUpdate:
    id: int
    email: str
    class_year: int
    first_name: str
    last_name: str
    program_id: int
    avatar_url: str
    bio: str
    display_name: str
