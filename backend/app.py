import logging
import os
import random
from functools import wraps

import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS

import matcher
from entities.user import UserUpdate, OnboardingStatus
from entities.group import DatabaseGroup, GroupCommitmentOptions
from util import generate_database_user, send_email
from integration import reformat_user_payload, convert_user_to_profile, reformat_user_skills, reformat_user_preferences, \
    reformat_join_matchround_resp
import db
import re
import time
import jwt
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.config["JWT_ISSUER"] = "uwfs"  # Issuer of tokens
app.config["JWT_AUTHTYPE"] = "HS256"  # HS256, HS512, RS256, or RS512
app.config["JWT_SECRET"] = os.environ.get('JWT_SECRET')  # string for HS256/HS512, bytes (RSA Private Key) for RS256/RS512
app.config["JWT_AUTHMAXAGE"] = 3600
app.config["JWT_REFRESHMAXAGE"] = 604800

CORS(app)
config = {}
otp_map = {}


def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if token is None:
            return jsonify({'message': 'Missing x-access-token header.'}), 401

        try:
            data = jwt.decode(token, app.config['JWT_SECRET'])
            user_id = db.get_user_by_id(data['id'])
            if user_id is None:
                raise Exception("User doesn't exist")
        except jwt.ExpiredSignatureError:
            return jsonify({
                'message': 'Expired jwt.'
            }), 401
        except:
            return jsonify({
                'message': 'Invalid jwt.'
            }), 401

        return f(user_id, *args, **kwargs)

    return decorated


@app.route('/')
def hello_world():  # put application's code here
    return {
        "message": "FirstStep API v1"
    }


@app.post('/register')
def register():
    data = request.get_json()
    if db.get_user(data["email"]):
        return jsonify({"error": "Email is already registered."}), 200

    email_regex = re.compile(r"[^@]+@uwaterloo.ca")
    if not email_regex.match(data["email"]):
        return jsonify({"error": "Invalid email."}, 200)

    otp = str(random.randint(0, 999999)).zfill(6)
    otp_map[data["email"]] = (otp, int(time.time()) + 600)

    send_email("Your FirstStep Verification Code",
               f"Thanks for signing up for FirstStep!\n\n"
               f"Your verification code is {otp}.\n\n"
               f"This code will expire in 10 minutes.",
               os.environ.get('EMAIL_USER'),
               [data["email"]],
               os.environ.get('EMAIL_PASS'))

    logging.info(f"Sent verification email to {data} [{otp}]")
    return jsonify({"message": f"Verification email sent to {data['email']}."}), 200


@app.post('/login')
def login():
    data = request.get_json()
    if not db.get_user(data["email"]):
        return jsonify({"error": "Invalid credentials."}), 200

    user_id = db.get_user(data["email"])['id']
    if not bcrypt.checkpw(data["password"].encode('utf-8'), db.get_hashed_password(user_id).encode('utf-8')):
        return jsonify({"error": "Invalid credentials."}), 200

    token = jwt.encode({'id': user_id}, app.config['JWT_SECRET'])
    return jsonify({"token": token}), 200


# Just delete the token from client's session storage / cookies
# @require_jwt
# @app.post('/logout')
# def logout(user_id):
#     return jsonify({"message": "ok"}, 200)

@app.post('/user')
def create_user():
    data = request.get_json()
    otp = data["otp"]

    if data["email"] not in otp_map:
        return jsonify({"message": "No verfication code was requested for this email."}), 200

    otp_check = otp_map[data["email"]]

    real = otp_check[0]
    expire = otp_check[1]
    cur_time = int(time.time())
    if cur_time > expire:
        del otp_check[data["email"]]
        return jsonify({"error": "Verification code is expired."}), 200
    if not otp == real:
        return jsonify({"error": "Verification code is incorrect."}), 200

    password = data["password"]
    if not 8 <= len(password) <= 32:
        return jsonify({"error": "Password must be between 8 to 32 characters."}), 200

    user = UserUpdate(
        id=0,  # unused
        email=data["email"],
        class_year=data['classYear'],
        first_name=data['firstName'],
        last_name=data['lastName'],
        program_id=data['program']["id"],
        avatar_url=data['avatarURL'],
        bio=data['bio'],
        display_name=data['displayName']
    )
    user_id = db.create_user(user, password)

    del otp_map[data["email"]]
    return jsonify({"id": user_id}), 201


@app.get('/user/profile')
@require_jwt
def get_user():
    email = request.args.get("email")
    user = db.get_user(email)
    formatted_user = reformat_user_payload(user)
    return jsonify(formatted_user), 200


@app.post('/user/profile')
@require_jwt
def update_user(user_id):
    data = request.get_json()
    json_body = data["newProfile"]
    user = UserUpdate(
        id=user_id,
        email=json_body["email"],
        class_year=json_body["classYear"],
        first_name=json_body["firstName"],
        last_name=json_body["lastName"],
        program_id=json_body["program"]["id"],
        avatar_url=(json_body["avatarURL"] if "avatarURL" in json_body else ""),
        # TODO temporary workaround, without ORM, hard to insert NULL
        display_name=json_body["displayName"],
        bio=(json_body["bio"] if "bio" in json_body else "")
    )
    db.update_user(user)
    updated_user = db.get_user_by_id(user_id)
    db.update_user_onboarding(user_id, OnboardingStatus.Step1.value)
    updated_profile = convert_user_to_profile(updated_user)
    payload = {'updatedProfile': updated_profile, 'userId': user_id}
    return jsonify(payload), 200


@app.get('/user/skillsets')
@require_jwt
def get_user_skillsets():
    user_id = request.args.get("userId")
    rows = db.get_user_skillsets(user_id)
    data = {"userId": user_id, "skillsets": reformat_user_skills(rows)}
    return jsonify(data), 200


@app.get('/user/preferences')
@require_jwt
def get_user_preferences():
    user_id = request.args.get("userId")
    rows = db.get_user_preferences(user_id)
    data = {"userId": user_id, "preferences": reformat_user_preferences(rows)}
    return jsonify(data), 200


@app.post('/user/skillsets')
@require_jwt
def update_user_skillsets():
    data = request.get_json()
    user_id = data["userId"]
    skillsets = data["newSkillsets"]
    db.update_user_skills(user_id, skillsets)
    db.update_user_onboarding(user_id, OnboardingStatus.Step2.value)
    rows = db.get_user_skillsets(user_id)
    payload = {"userId": user_id, "updatedSkillsets": reformat_user_skills(rows)}
    return jsonify(payload), 200


@app.post('/user/preferences')
@require_jwt
def update_user_preferences():
    data = request.get_json()
    user_id = data["userId"]
    preferences = data["newPreferences"]
    db.update_user_preferences(user_id, preferences)
    db.update_user_onboarding(user_id, OnboardingStatus.Completed.value)
    rows = db.get_user_preferences(user_id)
    payload = {"userId": user_id, "updatedPreferences": reformat_user_preferences(rows)}
    return jsonify(payload), 200


@app.post('/user/matching/join')
@require_jwt
def update_user_matching_join():
    data = request.get_json()
    user_id = data["userId"]
    match_round_id = data["matchroundId"]
    data = db.add_user_to_matching_round(user_id, match_round_id)
    return jsonify(reformat_join_matchround_resp(user_id, data)), 200


@app.post('/user/matching/leave')
@require_jwt
def update_user_matching_leave():
    data = request.get_json()
    user_id = data["userId"]
    match_round_id = data["matchroundId"]
    db.remove_user_from_matching_round(user_id, match_round_id)
    payload = {
        'userId': user_id,
        'matchroundId': match_round_id,
        'success': True
    }
    return jsonify(payload), 200


@app.delete('/user/profile')
@require_jwt
def delete_user():
    user_id = request.args.get("userId")
    db.delete_user(user_id)
    return jsonify({"deleted": True}), 200


@app.post('/group')
@require_jwt
def create_group():
    data = request.get_json()
    group = DatabaseGroup(
        id=0,  # unused
        name=data['name'],
        is_group_permanent=data["isPermanent"],
        date_of_creation=data["creationDate"],
        members=data['members']
    )
    group_id = db.create_group(group)
    return jsonify({"id": group_id}), 201


@app.get('/group/profile')
@require_jwt
def get_group():
    user_id = request.args.get("userId")
    response = db.get_group_by_user_id(user_id)
    return jsonify({'userId': user_id, 'group': response}), 200


@app.post('/group/profile')
@require_jwt
def update_group():
    data = request.get_json()
    group = DatabaseGroup(
        id=data["id"],
        name=data["name"],
        is_group_permanent=data["isPermanent"],
        date_of_creation=None,
        members=None,
    )
    db.update_group(group)
    return '', 204


@app.post('/group/members')
@require_jwt
def update_members(user):
    data = request.get_json()
    group_id = data["id"]
    members = data["members"]
    db.update_members(group_id, members)
    return '', 204


# not used?
@app.post('/group/matching')
@require_jwt
def group_commitment(user_id):
    data = request.get_json()
    commitment = False if data["action"] == 0 else True
    db.group_commitment(user_id, data["groupId"], commitment)
    return '', 204


@app.post('/group/commitment')
@require_jwt
def commit_group(user_id):
    data = request.get_json()
    # temporary patches, no idea why the endpoint above it exists
    group_id = data["groupId"]

    if not db.get_user_by_id(user_id)['group_id'] == group_id:
        return jsonify({'error': 'User does not belong to this group.'}), 200

    action = data['action']
    hasGroup = True
    # reason = data['reason'] # unused, should be logged somewhere
    if action == GroupCommitmentOptions.Commit.value:
        # db.commit_group(data["groupId"], data["commit"])
        pass
    elif action == GroupCommitmentOptions.Leave.value:
        db.group_commitment(user_id, group_id, False)
        hasGroup = False
    updated_group = db.get_group_by_user_id(user_id)
    response = {'userId': user_id, 'hasGroup': hasGroup, 'group': updated_group}
    return jsonify(response), 200


@app.delete('/group/profile')
@require_jwt
def delete_group(user_id):
    group_id = request.args.get("groupId")
    if not db.get_user_by_id(user_id)['group_id'] == group_id:
        return jsonify({'error': 'User does not belong to this group.'}), 200
    db.delete_group(group_id)
    return jsonify({"deleted": True}), 200


@app.get('/global/matching/current')
def get_matching_round():
    result = db.get_matching_rounds()
    data = {"matchRounds": result}
    return jsonify(data), 200


@app.get('/global/skillsets/all')
def get_all_skillsets():
    result = db.get_all_skillsets()
    data = {"skillsets": result}
    return jsonify(data), 200


@app.get('/global/preferences/all')
def get_all_preferences():
    result = db.get_all_preferences()
    data = {"preferences": result}
    return jsonify(data), 200


@app.get('/global/programs/all')
def get_all_programs():
    result = db.get_all_programs()
    data = {"programs": result}
    return jsonify(data), 200


@app.post('/onboarding/validate_email')
def validate_email():
    data = request.get_json()
    email_regex = re.compile(r"[^@]+@uwaterloo.ca")
    valid_email = False
    if email_regex.match(data["email"]):
        valid_email = True
    return jsonify({"is_new_valid_email": valid_email, "rejection_reason": None}), 200


def init():
    global config
    config['POSTGRES_HOST'] = os.environ.get('POSTGRES_HOST') if os.environ.get('POSTGRES_HOST') else 'localhost'
    config['POSTGRES_PORT'] = int(os.environ.get('POSTGRES_PORT')) if os.environ.get('POSTGRES_PORT') else 5432
    config['POSTGRES_USER'] = os.environ.get('POSTGRES_USER') if os.environ.get('POSTGRES_USER') else 'fs'
    config['POSTGRES_PASSWORD'] = os.environ.get('POSTGRES_PASSWORD') if os.environ.get(
        'POSTGRES_PASSWORD') else 'default'
    config['POSTGRES_DB'] = os.environ.get('POSTGRES_DB') if os.environ.get('POSTGRES_DB') else 'master'

    logging.basicConfig(level=logging.INFO)

    connections = db.init_db(config['POSTGRES_HOST'], config['POSTGRES_PORT'], config['POSTGRES_USER'],
                             config['POSTGRES_PASSWORD'], config['POSTGRES_DB'])

    retry_limit = 10
    for _ in range(retry_limit):
        try:
            if connections:
                # Generate 50 users with mock data if no users are in the table
                users = db.get_all_users()

                if users is None:
                    test_user = generate_database_user()
                    test_user.email = 'admin@uwaterloo.ca'
                    logging.info('Create test users...')
                    db.create_user(test_user, 'lifeisbigcat', mock=True)
                    for i in range(49):
                        user = generate_database_user()
                        db.create_user(user, 'lifeisbigcat', mock=True)
                    logging.info('Finished creating test users.')
            break
        except:
            logging.warning("Connection pool not ready. Trying again in 1 second.")
            time.sleep(1)

    # Start matching cronjob
    matcher.init()

if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', threaded=True)
