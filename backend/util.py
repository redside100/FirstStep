from typing import List

from entities.user import User, UserUpdate, Rating
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
            u.in_group = True
            users.remove(u)
            partial_group.members.append(u)
        
        groups.append(partial_group)
    
    if not n % size == 0:
        overflow = random.sample(groups, n % size)
        for i in range(n % size):
            overflow[i].members.append(users[i])
    
    return groups

def a_prefer_b1_b2(a: User, b1: User, b2: User):
    sorted_ratings = a.ratings.get_ratings_sorted()
    for rating_pair in sorted_ratings:
        if b1.ratings.get_rating(rating_pair[1]) > b2.ratings.get_rating(rating_pair[1]):
            return b1
        elif b2.ratings.get_rating(rating_pair[1]) > b1.ratings.get_rating(rating_pair[1]):
            return b2
    
    return b1

def generate_test_user(user_id=None):
    programs = ["ELEC", "COMP", "MECH", "ARCH", "CIVIL"]
    current_time = int(time.time())
    if not user_id:
        user_id = random.randint(1, 999999)
    current_time = time.time()
    return User(
        id=user_id,
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