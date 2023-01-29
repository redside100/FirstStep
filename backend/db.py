import logging
import time
import random

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from functools import wraps

from integration import convert_user_to_profile

connection_pool = None

MIN_CONNECTIONS = 0
MAX_CONNECTIONS = 50
CONNECTION_TIMEOUT = 25
def init_db(host, port, user, password, database):
    global connection_pool
    for _ in range(CONNECTION_TIMEOUT):
        try:
            connection_pool = pool.ThreadedConnectionPool(MIN_CONNECTIONS, MAX_CONNECTIONS, user=user, password=password, host=host, port=port, database=database)
            break
        except psycopg2.OperationalError:
            logging.warning("Could not connect to postgres, retrying in 1 second")
            time.sleep(1)

    if not connection_pool:
        logging.error(f"Couldn't connect to postgres (within {CONNECTION_TIMEOUT} seconds)")
    else:
        logging.info("Connected to postgres.")
    return connection_pool

def get_connection():
    conn = connection_pool.getconn()
    return conn.cursor(cursor_factory=RealDictCursor), conn

def clean_connection(cursor, conn):
    cursor.close()
    connection_pool.putconn(conn)

# TODO connection_pool.closeall

def use_connection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cursor, conn = get_connection()
        result = f(cursor, conn, *args, **kwargs)
        clean_connection(cursor, conn)
        return result
    return decorated_function

@use_connection
def get_matching_rounds(cursor, connection):
    cursor.execute("SELECT * FROM MatchRounds")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def get_all_users(cursor, connection):
    cursor.execute("SELECT * FROM Users")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def get_all_groups(cursor, connection):
    cursor.execute("SELECT * FROM Groups")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def get_all_skillsets(cursor, connection):
    cursor.execute("SELECT * FROM Skillsets")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def get_all_preferences(cursor, connection):
    cursor.execute("SELECT * FROM Preferences")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def get_all_programs(cursor, connection):
    cursor.execute("SELECT * FROM Programs")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def get_user(cursor, connection, email):
    cursor.execute(f"SELECT * FROM Users WHERE email = '{email}'")
    data = cursor.fetchone()
    if data:
        if data["program_id"] is not None:
            program_id = data["program_id"]
            cursor.execute(f"SELECT * From Programs WHERE id = {program_id}")
            data["program"] = cursor.fetchone()
        # remove foreign key ids from the request (not needed)
        del data["program_id"]
        user_id = data["id"]
        cursor.execute(f"SELECT onboarding_status, is_verified, is_eligible FROM UserOnboarding WHERE user_id = {user_id}")
        data["onboarding"] = cursor.fetchone()
        return data
    return None

@use_connection
def _get_user_by_id(cursor, connection, id):
    cursor.execute(f"SELECT * FROM Users WHERE id = '{id}'")
    data = cursor.fetchone()
    if data:
        if data["program_id"] is not None:
            program_id = data["program_id"]
            cursor.execute(f"SELECT * From Programs WHERE id = {program_id}")
            data["program"] = cursor.fetchone()
        # remove foreign key ids from the request (not needed)
        del data["program_id"]
        user_id = data["id"]
        cursor.execute(f"SELECT onboarding_status, is_verified, is_eligible FROM UserOnboarding WHERE user_id = {user_id}")
        data["onboarding"] = cursor.fetchone()
        return data
    return None

@use_connection
def get_user_skillsets(cursor, connection, user_id):
    cursor.execute(f"SELECT skill_id, rating from UserSkills WHERE user_id = {user_id}")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def get_user_preferences(cursor, connection, user_id):
    cursor.execute(f"SELECT preference_id, preferred from UserPreferences WHERE user_id = {user_id}")
    data = cursor.fetchall()
    if data:
        return data
    return None

@use_connection
def _get_group(cursor, connection, group_id):
    cursor.execute(f"SELECT * FROM Groups WHERE id = {group_id}")
    data = cursor.fetchone()

    if data:
        cursor.execute(f"SELECT * from Users WHERE group_id = {group_id}")
        members = cursor.fetchall()
        users = []
        for member in members:
            users.append(_get_user_by_id(member['id']))
        data["members"] = []
        for user in users:
            data["members"].append(convert_user_to_profile(user))
        return data
    return None

@use_connection
def get_group_by_user_id(cursor, connection, user_id):
    cursor.execute(f"SELECT * FROM Users WHERE id = {user_id}")
    user = cursor.fetchone()
    return _get_group(user['group_id'])


@use_connection
def create_user(cursor, connection, user, mock=False):
    cursor.execute(f"INSERT INTO "
                   f"Users (email, class_year, first_name, last_name, program_id, avatar_url, bio, display_name)"
                   f"VALUES "
                   f"('{user.email}', {user.class_year}, '{user.first_name}', '{user.last_name}', '{user.program_id}',"
                   f"'{user.avatar_url}', '{user.bio}', '{user.display_name}') RETURNING id")
    user_id = cursor.fetchone()["id"]

    skillsets = len(get_all_skillsets())
    for i in range(skillsets):
        if not mock:
            cursor.execute(f"INSERT INTO UserSkills(rating, user_id, skill_id) VALUES (0, {user_id}, {i + 1})")
        else:
            cursor.execute(f"INSERT INTO UserSkills(rating, user_id, skill_id) VALUES ({random.randint(1, 5)}, {user_id}, {i + 1})")

    preferences = len(get_all_preferences())
    for i in range(preferences):
        cursor.execute(f"INSERT INTO UserPreferences(preferred, user_id, preference_id) VALUES (FALSE, {user_id}, {i + 1})")

    cursor.execute(f"INSERT INTO UserOnboarding VALUES ({user_id}, 0, FALSE, FALSE)")
    connection.commit()
    return user_id

@use_connection
def update_user(cursor, connection, user):
    cursor.execute(f"UPDATE Users SET first_name = '{user.first_name}',"
                   f"last_name = '{user.last_name}', email = '{user.email}', class_year = {user.class_year},"
                   f" program_id = {user.program_id}, avatar_url = '{user.avatar_url}',"
                   f" bio = '{user.bio}', display_name = '{user.display_name}' WHERE id = {user.id}")
    connection.commit()

@use_connection
def create_group(cursor, connection, group):
    cursor.execute(f"INSERT INTO Groups (name, is_group_permanent, date_of_creation)"
                   f" VALUES ('{group.name}', {group.is_group_permanent},"
                   f" '{group.date_of_creation}') RETURNING id")
    group_id = cursor.fetchone()["id"]
    for member in group.members:
        cursor.execute(f"UPDATE Users SET group_id = {group_id} WHERE id = {member}")
    connection.commit()
    return group_id

@use_connection
def update_group(cursor, connection, group):
    cursor.execute(f"UPDATE Groups SET name = '{group.name}', is_group_permanent = {group.is_group_permanent}"
                   f" WHERE id = {group.id}")
    connection.commit()

@use_connection
def update_members(cursor, connection, group_id, group_members):
    # Remove old members
    cursor.execute(f"UPDATE Users SET group_id = NULL WHERE group_id = {group_id}")
    for member in group_members:
        cursor.execute(f"UPDATE Users SET group_id = {group_id} WHERE id = {member}")
    connection.commit()

@use_connection
def delete_user(cursor, connection, user_id):
    cursor.execute(f"DELETE FROM UserSkills WHERE user_id = {user_id}")
    cursor.execute(f"DELETE FROM UserPreferences WHERE user_id = {user_id}")
    cursor.execute(f"DELETE FROM UserOnboarding WHERE user_id = {user_id}")
    cursor.execute(f"DELETE FROM Users WHERE id = {user_id}")
    connection.commit()

@use_connection
def delete_group(cursor, connection, group_id):
    cursor.execute(f"UPDATE Users SET group_id = NULL WHERE group_id = {group_id}")
    cursor.execute(f"DELETE FROM Groups WHERE id = {group_id}")
    connection.commit()

@use_connection
def group_commitment(cursor, connection, user_id, group_id, action):
    if not action:
        cursor.execute(f"UPDATE Users SET group_id = NULL WHERE id = {user_id}")
    elif action:
        cursor.execute(f"UPDATE Users SET group_id = {group_id} WHERE id = {user_id}")
    connection.commit()

@use_connection
def commit_group(cursor, connection, group_id, commitment):
    cursor.execute(f"UPDATE Groups SET is_group_permanent = {commitment} WHERE id = {group_id}")
    connection.commit()

@use_connection
def update_user_skills(cursor, connection, user_id, skillsets):
    for skills in skillsets:
        skill_rating = skills["data"]
        skill_id = skills["attributeId"]
        cursor.execute(f"UPDATE UserSkills SET rating = {skill_rating}"
                       f" WHERE user_id = {user_id} AND skill_id = {skill_id}")
    connection.commit()

@use_connection
def update_user_preferences(cursor, connection, user_id, preferences):
    for preference in preferences:
        preference_data = preference["data"]
        preference_id = preference["attributeId"]
        cursor.execute(f"UPDATE UserPreferences SET preferred = {preference_data}"
                       f" WHERE user_id = {user_id} AND preference_id = {preference_id}")
    connection.commit()

@use_connection
def add_user_to_matching_round(cursor, connection, user_id, match_round_id):
    cursor.execute(f"UPDATE Users SET match_round_id = {match_round_id} WHERE id = {user_id}")
    connection.commit()
    cursor.execute(f"SELECT * FROM MatchRounds WHERE id = {match_round_id}")
    data = cursor.fetchone()
    if data:
        return data
    return None

@use_connection
def remove_user_from_matching_round(cursor, connection, user_id, match_round_id):
    cursor.execute(f"UPDATE Users SET match_round_id = NULL"
                   f" WHERE id = {user_id} AND match_round_id = {match_round_id}")
    connection.commit()