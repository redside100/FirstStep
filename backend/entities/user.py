from dataclasses import dataclass


@dataclass
class Rating:
    software: float
    leadership: float
    database: float
    writing: float
    hardware: float
    embedded: float

    def as_tuple(self):
        return self.software, self.leadership, self.database, self.writing, self.hardware, self.embedded

    @staticmethod
    def from_tuple(obj):
        return Rating(obj[0], obj[1], obj[2], obj[3], obj[4], obj[5])

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

    def __sub__(self, other):
        return Rating(
            software=self.software - other.software,
            leadership=self.leadership - other.leadership,
            database=self.database - other.database,
            writing=self.writing - other.writing,
            hardware=self.hardware - other.hardware,
            embedded=self.embedded - other.embedded
        )

    def __add__(self, other):
        return Rating(
            software=self.software + other.software,
            leadership=self.leadership + other.leadership,
            database=self.database + other.database,
            writing=self.writing + other.writing,
            hardware=self.hardware + other.hardware,
            embedded=self.embedded + other.embedded
        )

    def mul(self, const):
        return Rating(
            software=self.software * const,
            leadership=self.leadership * const,
            database=self.database * const,
            writing=self.writing * const,
            hardware=self.hardware * const,
            embedded=self.embedded * const
        )

    def div(self, const):
        return Rating(
            software=self.software / const,
            leadership=self.leadership / const,
            database=self.database / const,
            writing=self.writing / const,
            hardware=self.hardware / const,
            embedded=self.embedded / const
        )

    def avg(self):
        return (self.software + self.leadership + self.database + self.writing + self.hardware + self.embedded) / 6

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