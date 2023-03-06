import logging
from datetime import datetime

import db
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from entities.group import DatabaseGroup
from entities.rating import Rating
from entities.user import User
from util import create_groups, get_next_matchtime, get_next_debug_matchtime, gen_random_team_name
from consts import *

scheduler = None
current_matchround_id = None
last_matchround_id = None
MATCHER_DEBUG = False


def init():
    global scheduler
    global current_matchround_id
    scheduler = BackgroundScheduler(timezone='UTC')
    # 4 pm UTC, 12 pm EST
    if not MATCHER_DEBUG:
        scheduler.add_job(cleanup_groups, trigger=CronTrigger(hour='15', day='*/2'), args=[True])
        scheduler.add_job(match, trigger=CronTrigger(hour='16'))
        start_time = get_next_matchtime()
        current_matchround_id = db.create_matchround(status=2, next_status=3, start=start_time, next_start=start_time + 1,
                                                     next_end=start_time + 30)
    else:
        scheduler.add_job(cleanup_groups, trigger=CronTrigger(minute='*/2'), args=[True])
        scheduler.add_job(match, trigger=CronTrigger(second='15'))
        start_time = get_next_debug_matchtime()
        current_matchround_id = db.create_matchround(status=2, next_status=3, start=start_time, next_start=start_time + 1,
                                                     next_end=start_time + 30)
        logging.warning('Matcher is in debug mode! Groups will be made and deleted every minute!')

    scheduler.start()
    logging.info('Matching scheduler initialized!')


def match():
    global current_matchround_id
    global last_matchround_id
    if not db.connection_pool:
        logging.error('No postgres connection, cannot match users')
        return

    deleted = cleanup_groups(False)
    next_matchtime = get_next_matchtime()

    # update current status
    if current_matchround_id is not None:
        current_time = int(time.time())
        db.update_matchround(current_matchround_id, status=3, next_status=4, start=current_time,
                             next_start=current_time + 10, next_end=next_matchtime)

    users = []
    for db_user in db.get_all_users():
        if not db_user['match_round_id'] == 0:
            users.append(User.from_database(
                db_user, Rating.from_database(
                    db.get_user_skillsets(db_user['id'])
                )
            ))

    groups = 0
    if users:
        n = len(users)
        max_groups = int((n / MIN_GROUP_SIZE + n / MAX_GROUP_SIZE) / 2)
        groups = create_groups(users, min_size=MIN_GROUP_SIZE, max_size=MAX_GROUP_SIZE, max_groups=max_groups)

        if groups is not None:
            for group in groups:
                db_group = DatabaseGroup(0, gen_random_team_name(), False, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                                        [user.id for user in group.members])
                db.create_group(db_group)

            logging.info(f'Created {len(groups)} new groups.')
        else:
            logging.warning('No groups were made (not enough users?)')
    else:
        logging.warning('No eligible users for matching round.')

    current_time = int(time.time())
    # set to teams assigned for current match round
    if current_matchround_id is not None:
        db.update_matchround(current_matchround_id, status=4, next_status=5, start=current_time,
                             next_start=next_matchtime, next_end=next_matchtime)

    # close out last match round
    if last_matchround_id is not None:
        db.update_matchround(last_matchround_id, status=5, next_status=5, start=current_time, next_start=current_time, next_end=current_time)

    last_matchround_id = current_matchround_id

    # create a new match round entry
    if not MATCHER_DEBUG:
        start_time = get_next_matchtime()
        current_matchround_id = db.create_matchround(status=2, next_status=3, start=start_time, next_start=start_time + 1,
                                                     next_end=start_time + 30)
    else:
        start_time = get_next_debug_matchtime()
        current_matchround_id = db.create_matchround(status=2, next_status=3, start=start_time, next_start=start_time + 1,
                                                     next_end=start_time + 30)

    return len(groups) if groups else 0, deleted


def cleanup_groups(delete_permanent):
    if not db.connection_pool:
        logging.error('No postgres connection, cannot get groups users')
        return 0

    groups = db.get_all_groups()

    if not groups:
        logging.info(f'No groups to delete.')
        return 0

    deleted = 0
    for group in groups:
        if group['is_group_permanent'] == delete_permanent:
            db.delete_group(group['id'])
            deleted += 1
    logging.info(f'Deleted {deleted} groups. Permanent = {delete_permanent}')

    return deleted
