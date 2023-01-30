from dataclasses import dataclass
from typing import List
from entities.user import User
from entities.rating import Rating
from enum import Enum

class GroupCommitmentOptions(Enum):
  Leave = 0 # a member leaves the group
  Commit = 1 # Votes to keep the group
  Undecided = 2 # ???

@dataclass
class Group:
    id: int
    name: str
    is_permanent: int
    members: List[User]

    def get_average_ratings(self):
        if len(self.members) > 0:
            return Rating(
                distributed=sum(u.ratings.distributed for u in self.members) / len(self.members),
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
    is_group_permanent: bool
    date_of_creation: str
    members: List[int]

