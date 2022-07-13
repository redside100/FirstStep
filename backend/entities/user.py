from dataclasses import dataclass


@dataclass
class Rating:
    software: float
    leadership: float
    database: float
    writing: float
    hardware: float
    embedded: float

    def get_rating(self, rating: str):
        match rating.lower():
            case 'software':
                return self.software
            case 'leadership':
                return self.leadership
            case 'database':
                return self.database
            case 'writing':
                return self.writing
            case 'hardware':
                return self.hardware
            case 'embedded':
                return self.embedded
            case _:
                return 0

    def get_ratings_sorted(self):
        base = [(self.software, 'software'),
        (self.leadership, 'leadership'),
        (self.database, 'database'),
        (self.writing, 'writing'),
        (self.hardware, 'hardware'),
        (self.embedded, 'embedded')]
        base.sort()
        return base

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
