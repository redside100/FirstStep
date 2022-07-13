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
        rating = rating.lower()
        if rating == 'software':
            return self.software
        elif rating == 'leadership':
            return self.leadership
        elif rating == 'database':
            return self.database
        elif rating == 'writing':
            return self.writing
        elif rating == 'hardware':
            return self.hardware
        elif rating == 'embedded':
            return self.embedded

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
