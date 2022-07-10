from dataclasses import dataclass
from typing import List
from user import User


@dataclass
class Group:
    id: int
    name: str
    expire: int
    members: List[User]
