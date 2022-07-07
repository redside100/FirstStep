from typing import List

from entities.user import User, Rating
from entities.group import Group
import random
import names
import time

# Temporary impl. (completely random)
def create_groups(users: List[User], size=4):
    n = len(users)
    if n < size:
        return None

    groups = []
    for i in range(n // size):
        partial_group = Group(id=i, name=f"Test Group {i}", expire=9999999999, members=[])
        for j in range(size):
            u = random.choice(users)
            users.remove(u)
            partial_group.members.append(u)
        
        groups.append(partial_group)
    
    if not n % size == 0:
        overflow = random.sample(groups, n % size)
        for i in range(n % size):
            overflow[i].members.append(users[i])
    
    return groups

def generate_test_user():
    programs = ["ELEC", "COMP", "MECH", "ARCH", "CIVIL"]
    current_time = int(time.time())
    return User(
        id=random.randint(1, 999999),
        first_name=names.get_first_name(),
        last_name=names.get_last_name(),
        student_id=random.randint(100000, 999999),
        program=random.choice(programs),
        avatar_url="https://www.allaboutbirds.org/guide/assets/photo/59953191-480px.jpg",
        bio="Life is bigcat",
        ratings=Rating(
            software=random.randint(0, 5),
            leadership=random.randint(0, 5),
            database=random.randint(0, 5),
            writing=random.randint(0, 5),
            hardware=random.randint(0, 5),
            embedded=random.randint(0, 5)
        ),
        in_group=False,
        group_id=0,
        intent_stay=False,
        join_date=current_time
    )