from dataclasses import dataclass
from typing import List
from entities.user import User


@dataclass
class Group:
    id: int
    name: str
    expire: int
    members: List[User]


@dataclass
class DatabaseGroup:
    id: int
    name: str
    is_permanent: bool
    creation_date: str
    members: List[int]

