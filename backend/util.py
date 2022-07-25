from typing import List

from entities.user import User, UserUpdate, Rating
from entities.group import Group
import random
import logging
import names
import time
from mip import *


def split_list(l, n):
    for i in range(0, n):
        yield l[i::n]


def add_ratings(ratings):
    rating = Rating(0, 0, 0, 0, 0, 0)
    for r in ratings:
        rating += r
    return rating


# (Linear) Integer programming algorithm
# Minimize "variance" between summed group ratings
def create_groups(users: List[User], min_size=4, max_size=5, max_groups=None, timeout=300):
    n = len(users)
    if n < min_size:
        return None

    max_group_num = n // min_size
    if max_groups:
        max_group_num = max_groups

    m = Model()

    # x[i][j] = 1 => j'th user is part of group i
    x = [[m.add_var(var_type=BINARY) for _ in range(n)] for _ in range(max_group_num)]

    # Each group must be between min and max size (or empty)
    for i in range(max_group_num):
        m += xsum(x[i][j] for j in range(n)) >= min_size or xsum(x[i][j] for j in range(n)) == 0
        m += xsum(x[i][j] for j in range(n)) <= max_size

    # Each user cannot be in more than one group
    for j in range(n):
        m += xsum(x[i][j] for i in range(max_group_num)) == 1
    
    # Every user must be included in a group
    m += xsum(x[i][j] for i in range(max_group_num) for j in range(n)) == n

    # summed ratings for all groups
    data = [add_ratings([users[j].ratings.mul(x[i][j]) for j in range(n)]) for i in range(max_group_num)]

    # gonna be honest i'm 99% sure this is wrong but it looks like it works
    mean = add_ratings(data).div(len(data))
    # fake variance (can't square a linear expression)
    variance = add_ratings([(r - mean) for r in data]).div(len(data))

    m.objective = minimize(variance.avg())

    m.verbose = 0
    m.optimize(max_seconds=timeout)

    try:
        x[0][0].x
    except exceptions.SolutionNotAvailable:
        logging.error(f"Couldn't find a solution to group matching model (min {min_size}, max {max_size}, {n} users, max {max_group_num} groups)")
        return []

    groups = []

    for i in range(max_group_num):
        partial_group = Group(id=i, name=f"Test Group {i}", is_permanent=False, members=[])
        for j in range(n):
            if x[i][j].x == 1.0:
                partial_group.members.append(users[j])

        if partial_group.members:
            groups.append(partial_group)

    return groups


def generate_test_user(user_id=None):
    programs = ["ELEC", "COMP", "MECH", "ARCH", "CIVIL"]
    if not user_id:
        user_id = random.randint(1, 999999)
    current_time = int(time.time())
    return User(
        id=user_id,
        first_name=names.get_first_name(),
        last_name=names.get_last_name(),
        program=random.choice(programs),
        avatar_url="https://www.allaboutbirds.org/guide/assets/photo/59953191-480px.jpg",
        bio="Life is bigcat",
        ratings=Rating(
            distributed=random.randint(1, 5),
            leadership=random.randint(1, 5),
            database=random.randint(1, 5),
            writing=random.randint(1, 5),
            hardware=random.randint(1, 5),
            embedded=random.randint(1, 5)
        ),
        group_id=0
    )


def generate_database_user():
    programs = [1, 2, 3]
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    return UserUpdate(
        id=0,  # unused due to auto increment generation
        email=f"{first_name}_{last_name}@uwaterloo.ca",
        class_year=random.randint(2020, 2030),
        first_name=first_name,
        last_name=last_name,
        program_id=random.choice(programs),
        avatar_url="https://www.allaboutbirds.org/guide/assets/photo/59953191-480px.jpg",
        bio="Life is bigcat",
        display_name=f"{first_name}-{last_name}{random.randint(0, 100)}"
    )