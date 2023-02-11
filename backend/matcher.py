import logging
from datetime import datetime

import db
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from entities.group import DatabaseGroup
from entities.rating import Rating
from entities.user import User
from util import create_groups
from consts import *

scheduler = None

MATCHER_DEBUG = False


def init():
    global scheduler
    scheduler = BackgroundScheduler(timezone='UTC')
    # 4 pm UTC, 12 pm EST
    if not MATCHER_DEBUG:
        scheduler.add_job(cleanup_groups, trigger=CronTrigger(hour='15', day='*/2'), args=[True])
        scheduler.add_job(match, trigger=CronTrigger(hour='16'))
    else:
        scheduler.add_job(cleanup_groups, trigger=CronTrigger(minute='*/2'), args=[True])
        scheduler.add_job(match, trigger=CronTrigger(second='15'))
        logging.warning('Matcher is in debug mode! Groups will be made and deleted every minute!')

    scheduler.start()
    logging.info('Matching scheduler initialized!')


def match():
    if not db.connection_pool:
        logging.error('No postgres connection, cannot match users')
        return

    deleted = cleanup_groups(False)

    users = []
    for db_user in db.get_all_users():
        if not db_user['match_round_id'] == 0:
            users.append(User.from_database(
                db_user, Rating.from_database(
                    db.get_user_skillsets(db_user['id'])
                )
            ))

    if not users:
        logging.warning('No eligible users for matching round.')
        return

    n = len(users)
    max_groups = int((n / MIN_GROUP_SIZE + n / MAX_GROUP_SIZE) / 2)
    groups = create_groups(users, min_size=MIN_GROUP_SIZE, max_size=MAX_GROUP_SIZE, max_groups=max_groups)

    for group in groups:
        db_group = DatabaseGroup(0, 'New FYDP Group', False, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                                 [user.id for user in group.members])
        db.create_group(db_group)

    logging.info(f'Created {len(groups)} new groups.')

    return len(groups), deleted


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
