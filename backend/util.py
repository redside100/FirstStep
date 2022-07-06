from typing import List

from entities.user import User


def create_groups(users: List[User], size=4):
    n = len(users)
    if n < size:
        return None
