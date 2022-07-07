from typing import List

from entities.user import User
import random


# Temporary impl. (completely random)
def create_groups(users: List[User], size=4):
    n = len(users)
    if n < size:
        return None

    groups = []
    for i in range(n // size):
        partial_group = []
        for j in range(size):
            u = random.choice(users)
            users.remove(u)
            partial_group.append(u)
        
        groups.append(partial_group)
    
    if not n % size == 0:
        overflow = random.sample(groups, n % size)
        for i in range(n % size):
            overflow[i].append(users[i])
    
    return groups
        