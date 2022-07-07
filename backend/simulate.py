from util import create_groups, generate_test_user
from entities.user import User, Rating
import json

def dump_to_json(obj):
    with open(str(int(time.time())) + '_simulate.json', 'w+') as f:
        f.write(json.dumps(obj, default=lambda x: x.__dict__, indent=4))

def simulate_matching():
    users = []
    for i in range(50):
        users.append(generate_test_user())
    
    groups = create_groups(users)
    print(groups)
    dump_to_json(groups)

if __name__ == '__main__':
    simulate_matching()