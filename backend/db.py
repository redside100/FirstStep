import logging
import time

import psycopg2

connection = None
cursor = None
logger = logging.Logger("db")


def init_db(host, port, user, password, database):
    global connection
    global cursor
    for _ in range(10):
        try:
            connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
            cursor = connection.cursor()
            break
        except psycopg2.OperationalError:
            logger.warning("Could not connect to postgres, retrying in 1 second")
            time.sleep(1)

    if not connection:
        logger.error("Couldn't connect to postgres (within 10 seconds)")
    else:
        logger.info("Connected to postgres.")


def get_user(user_id):
    cursor.execute(f"SELECT * FROM Users WHERE id = {user_id}")
    data = cursor.fetchone()
    if data:
        return data
    return None


def create_user(user):
    cursor.execute("INSERT INTO Users "
                   "VALUES (%d, '%s', '%s', %d, '%s', '%s', '%s', %d, %d, %d, %d, %d, %d, '%s', '%s', '%s')" %
                   (user.group_id, user.first_name, user.last_name, user.student_id, user.program,
                    user.avatar_url, user.bio, user.ratings['software'], user.ratings['leadership'],
                    user.ratings['database'], user.ratings['writing'], user.ratings['hardware'],
                    user.ratings['embedded'], user.in_group, user.intent_stay, user.join_date))
    connection.commit()


def update_user(user):
    cursor.execute(f"UPDATE Users WHERE id = {user.id} SET first_name = {user.first_name},"
                   f" last_name = {user.last_name}, student_id = {user.student_id},"
                   f" program = {user.program}, avatar_url = {user.avatar_url}, bio = {user.bio}")
    connection.commit()


def get_group(group_id):
    cursor.execute(f"SELECT * FROM Groups WHERE id = {group_id}")
    data = cursor.fetchone()

    if data:
        return data
    return None


def create_group(group):
    cursor.execute("INSERT INTO Groups VALUES ('%s', %d)" % (group.name, group.expire))

    connection.commit()
