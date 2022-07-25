from dataclasses import dataclass
from consts import *
from entities.rating import Rating


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
