from util import create_groups, generate_test_user
from entities.user import User, Rating
import json
import time


def dump_to_json(obj):
    with open(str(int(time.time())) + '_simulate.json', 'w+') as f:
        f.write(json.dumps(obj, default=lambda x: x.__dict__, indent=4))


def simulate_matching():
    users = []
    for i in range(100):
        users.append(generate_test_user(i))

    n = len(users)
    groups = create_groups(users, min_size=4, max_size=5, max_groups=int((n / 4 + n / 5) / 2))

    print(f"Created {len(groups)} groups")
    data = [[] for _ in range(6)]
    print("Average Ratings Per Group")
    for group in groups:
        d = group.get_average_ratings()
        print(d, f"{len(group.members)} members")
        for i in range(6):
            data[i].append(d.as_tuple()[i])

    variances = []

    for category in data:
        if len(category) > 0:
            mean = sum(category) / len(category)
            deviations = [(x - mean) ** 2 for x in category]
            variances.append(sum(deviations) / len(category))

    # The lower the better
    print("Variance per category")
    print(variances)
    dump_to_json(groups)

if __name__ == '__main__':
    simulate_matching()