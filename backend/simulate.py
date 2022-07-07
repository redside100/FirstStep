from util import create_groups
from entities.user import User, Rating
import random
import names
import time
import json

def dump_to_json(obj):
    with open(str(int(time.time())) + '_simulate.json', 'w+') as f:
        f.write(json.dumps(obj, default=lambda x: x.__dict__, indent=4))

def simulate_matching():
    users = []
    programs = ["ELEC", "COMP", "MECH", "ARCH", "CIVIL"]
    current_time = int(time.time())
    for i in range(50):
        users.append(User(
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
        ))
    
    groups = create_groups(users)
    print(groups)
    dump_to_json(groups)

if __name__ == '__main__':
    simulate_matching()