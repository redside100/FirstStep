from dataclasses import dataclass
import string
from typing import List
from entities.user import User


@dataclass
class Group:
    id: int
    name: str
    expire: int
    members: List[User]
