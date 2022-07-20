from dataclasses import dataclass
from typing import List
from entities.user import User, Rating


@dataclass
class Group:
    id: int
    name: str
    expire: int
    members: List[User]

    def get_average_ratings(self):
        if len(self.members) > 0:
            return Rating(
                software=sum(u.ratings.software for u in self.members) / len(self.members),
                leadership=sum(u.ratings.leadership for u in self.members) / len(self.members),
                database=sum(u.ratings.database for u in self.members) / len(self.members),
                writing=sum(u.ratings.writing for u in self.members) / len(self.members),
                hardware=sum(u.ratings.hardware for u in self.members) / len(self.members),
                embedded=sum(u.ratings.embedded for u in self.members) / len(self.members)
            )
        return Rating(0, 0, 0, 0, 0, 0)


@dataclass
class DatabaseGroup:
    id: int
    name: str
    is_permanent: bool
    creation_date: str
    members: List[int]

