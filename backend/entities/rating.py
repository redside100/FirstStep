from dataclasses import dataclass
from consts import *

@dataclass
class Rating:
    distributed: float
    leadership: float
    database: float
    writing: float
    hardware: float
    embedded: float

    def as_tuple(self):
        return self.distributed, self.leadership, self.database, self.writing, self.hardware, self.embedded

    @staticmethod
    def from_tuple(obj):
        return Rating(obj[0], obj[1], obj[2], obj[3], obj[4], obj[5])

    @staticmethod
    def from_database(db_rows):
        rating = Rating(0, 0, 0, 0, 0, 0)
        for row in db_rows:
            if row['skill_id'] == DISTRIBUTED_SYSTEMS_ID:
                rating.distributed = row['rating']
            elif row['skill_id'] == LEADERSHIP_ID:
                rating.leadership = row['rating']
            elif row['skill_id'] == DATABASE_SYSTEMS_ID:
                rating.database = row['rating']
            elif row['skill_id'] == TECHNICAL_WRITING_ID:
                rating.writing = row['rating']
            elif row['skill_id'] == HARDWARE_ID:
                rating.hardware = row['rating']
            elif row['skill_id'] == EMBEDDED_SOFTWARE_ID:
                rating.embedded = row['rating']

        return rating

    def get_rating(self, rating: str):
        rating = rating.lower()
        if rating == 'distributed':
            return self.distributed
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
        base = [(self.distributed, 'distributed'),
        (self.leadership, 'leadership'),
        (self.database, 'database'),
        (self.writing, 'writing'),
        (self.hardware, 'hardware'),
        (self.embedded, 'embedded')]
        base.sort()
        return base

    def __sub__(self, other):
        return Rating(
            distributed=self.distributed - other.distributed,
            leadership=self.leadership - other.leadership,
            database=self.database - other.database,
            writing=self.writing - other.writing,
            hardware=self.hardware - other.hardware,
            embedded=self.embedded - other.embedded
        )

    def __add__(self, other):
        return Rating(
            distributed=self.distributed + other.distributed,
            leadership=self.leadership + other.leadership,
            database=self.database + other.database,
            writing=self.writing + other.writing,
            hardware=self.hardware + other.hardware,
            embedded=self.embedded + other.embedded
        )

    def mul(self, const):
        return Rating(
            distributed=self.distributed * const,
            leadership=self.leadership * const,
            database=self.database * const,
            writing=self.writing * const,
            hardware=self.hardware * const,
            embedded=self.embedded * const
        )

    def div(self, const):
        return Rating(
            distributed=self.distributed / const,
            leadership=self.leadership / const,
            database=self.database / const,
            writing=self.writing / const,
            hardware=self.hardware / const,
            embedded=self.embedded / const
        )

    def avg(self):
        return (self.distributed + self.leadership + self.database + self.writing + self.hardware + self.embedded) / 6