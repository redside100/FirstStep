from dataclasses import dataclass


@dataclass
class Rating:
    software: float
    leadership: float
    database: float
    writing: float
    hardware: float
    embedded: float


@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    student_id: int
    program: str
    avatar_url: str
    bio: str
    ratings: Rating
    in_group: bool
    group_id: int
    intent_stay: bool
    join_date: int
