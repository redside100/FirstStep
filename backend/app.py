import logging
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from authlib.integrations.flask_oauth2 import ResourceProtector
from validator import Auth0JWTBearerTokenValidator

import matcher
from entities.user import UserUpdate, OnboardingStatus
from entities.group import DatabaseGroup, GroupCommitmentOptions
from util import generate_database_user
from integration import reformat_user_payload, convert_user_to_profile, reformat_user_skills, reformat_user_preferences, reformat_join_matchround_resp
import db
import re
import time

APP_DOMAIN = "dev-vnfigzt6dhh6seoy.us.auth0.com"
APP_IDENTIFIER = "https://api.uwfs.live/"
require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    APP_DOMAIN,
    APP_IDENTIFIER
)
require_auth.register_token_validator(validator)


app = Flask(__name__)
CORS(app)
config = {}


@app.route('/')
@require_auth(None)
def hello_world():  # put application's code here
    return {
        "message": "FirstStep API v1"
    }


@app.post('/user')
@require_auth(None)
def create_user():
    data = request.get_json()
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
    user_id = db.create_user(user)
    return jsonify({"id": user_id}), 201


@app.get('/user/profile')
@require_auth(None)
def get_user():
    email = request.args.get("email")
    user = db.get_user(email)
    formatted_user = reformat_user_payload(user)
    return jsonify(formatted_user), 200

@app.post('/user/default')
@require_auth(None)
def get_or_create_user():
    data = request.get_json()
    email = data["email"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    user = db.get_user(email)
    if user is None:
        db.create_default_user(email, first_name, last_name)
        user = db.get_user(email)
    formatted_user = reformat_user_payload(user)
    return jsonify(formatted_user), 200


@app.post('/user/profile')
@require_auth(None)
def update_user():
    data = request.get_json()
    json_body = data["newProfile"]
    user_id = json_body["id"]
    user = UserUpdate(
        id=user_id,
        email=(json_body["email"] if "email" in json_body else ""),
        class_year=(json_body["classYear"] if "classYear" in json_body else ""),
        first_name=(json_body["firstName"] if "firstName" in json_body else ""),
        last_name=(json_body["lastName"] if "lastName" in json_body else ""),
        program_id=(json_body["program"]["id"] if "program" in json_body else ""),
        avatar_url=(json_body["avatarURL"] if "avatarURL" in json_body else ""), # TODO temporary workaround, without ORM, hard to insert NULL
        display_name=(json_body["displayName"] if "displayName" in json_body else ""),
        bio=(json_body["bio"] if "bio" in json_body else "")
    )
    db.update_user(user)
    updated_user = db.get_user_by_id(user_id)
    db.update_user_onboarding(user_id, OnboardingStatus.Step1.value)
    updated_profile = convert_user_to_profile(updated_user)
    payload = { 'updatedProfile': updated_profile, 'userId': user_id }
    return jsonify(payload), 200


@app.get('/user/skillsets')
@require_auth(None)
def get_user_skillsets():
    user_id = request.args.get("userId")
    rows = db.get_user_skillsets(user_id)
    data = { "userId": user_id, "skillsets": reformat_user_skills(rows) }
    return jsonify(data), 200


@app.get('/user/preferences')
@require_auth(None)
def get_user_preferences():
    user_id = request.args.get("userId")
    rows = db.get_user_preferences(user_id)
    data = { "userId": user_id, "preferences": reformat_user_preferences(rows) }
    return jsonify(data), 200


@app.post('/user/skillsets')
@require_auth(None)
def update_user_skillsets():
    data = request.get_json()
    user_id = data["userId"]
    skillsets = data["newSkillsets"]
    db.update_user_skills(user_id, skillsets)
    db.update_user_onboarding(user_id, OnboardingStatus.Step2.value)
    rows = db.get_user_skillsets(user_id)
    payload = { "userId": user_id, "updatedSkillsets": reformat_user_skills(rows) }
    return jsonify(payload), 200


@app.post('/user/preferences')
@require_auth(None)
def update_user_preferences():
    data = request.get_json()
    user_id = data["userId"]
    preferences = data["newPreferences"]
    db.update_user_preferences(user_id, preferences)
    db.update_user_onboarding(user_id, OnboardingStatus.Completed.value)
    rows = db.get_user_preferences(user_id)
    payload = { "userId": user_id, "updatedPreferences": reformat_user_preferences(rows) }
    return jsonify(payload), 200


@app.post('/user/matching/join')
@require_auth(None)
def update_user_matching_join():
    data = request.get_json()
    user_id = data["userId"]
    match_round_id = data["matchroundId"]
    data = db.add_user_to_matching_round(user_id, match_round_id)
    return jsonify(reformat_join_matchround_resp(user_id, data)), 200


@app.post('/user/matching/leave')
@require_auth(None)
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
@require_auth(None)
def delete_user():
    user_id = request.args.get("userId")
    db.delete_user(user_id)
    return jsonify({"deleted": True}), 200


@app.post('/group')
@require_auth(None)
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
@require_auth(None)
def get_group():
    user_id = request.args.get("userId")
    response = db.get_group_by_user_id(user_id)
    return jsonify({ 'userId': user_id, 'group': response }), 200


@app.post('/group/profile')
@require_auth(None)
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
@require_auth(None)
def update_members():
    data = request.get_json()
    group_id = data["id"]
    members = data["members"]
    db.update_members(group_id, members)
    return '', 204


@app.post('/group/matching')
@require_auth(None)
def group_commitment():
    data = request.get_json()
    commitment = False if data["action"] == 0 else True
    db.group_commitment(data["userId"], data["groupId"], commitment)
    return '', 204


@app.post('/group/commitment')
@require_auth(None)
def commit_group():
    data = request.get_json()
    # temporary patches, no idea why the endpoint above it exists
    user_id = data["userId"]
    group_id = data["groupId"]
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
    response = { 'userId': user_id, 'hasGroup': hasGroup, 'group': updated_group }
    return  jsonify(response), 200


@app.delete('/group/profile')
@require_auth(None)
def delete_group():
    group_id = request.args.get("groupId")
    db.delete_group(group_id)
    return jsonify({"deleted": True}), 200


@app.get('/global/matching/current')
@require_auth(None)
def get_matching_round():
    result = db.get_matching_rounds()
    data = { "matchRounds": result }
    return jsonify(data), 200


@app.get('/global/skillsets/all')
@require_auth(None)
def get_all_skillsets():
    result = db.get_all_skillsets()
    data = { "skillsets": result }
    return jsonify(data), 200


@app.get('/global/preferences/all')
@require_auth(None)
def get_all_preferences():
    result = db.get_all_preferences()
    data = { "preferences": result }
    return jsonify(data), 200


@app.get('/global/programs/all')
@require_auth(None)
def get_all_programs():
    result = db.get_all_programs()
    data = { "programs": result }
    return jsonify(data), 200


@app.post('/onboarding/validate_email')
@require_auth(None)
def validate_email():
    data = request.get_json()
    email_regex = re.compile(r"[^@]+@uwaterloo.ca")
    valid_email = False
    if email_regex.match(data["email"]):
        valid_email = True
    return jsonify({"is_new_valid_email": valid_email, "rejection_reason": None}), 200


@app.post('/debug')
def debug():
    secret: str = request.headers.get('uwfs-secret')
    if secret is None or secret != 'avocadoscado':
        return jsonify({"error": ":("}), 403

    data = request.get_json()
    cmd: str = data.get("cmd")

    args: str = data.get("args")

    if cmd is None:
        return jsonify({"error": "Missing cmd parameter."}), 400

    cmd = cmd.lower()
    if cmd == 'match':
        made, deleted = matcher.match()
        return jsonify({"message": f"Made {made} groups, deleted {deleted}."}), 200
    elif cmd == 'get_all_groups':
        return jsonify({"data": db.get_all_groups()}), 200
    elif cmd == 'get_all_users':
        return jsonify({"data": db.get_all_users()}), 200
    elif cmd == 'get_all_skillsets':
        return jsonify({"data": db.get_all_skillsets()}), 200
    elif cmd == 'get_user_skillsets':
        if args is None:
            return jsonify({"error": "Missing args parameter."}), 400
        if isinstance(args.get("id"), int):
            return jsonify({"data": db.get_user_skillsets(user_id=args.get("id"))}), 200
        else:
            return jsonify({"error": "Need args id parameter to be an integer."}), 200
    elif cmd == 'get_all_matchrounds':
        return jsonify({"data": db.get_all_matchrounds()}), 200
    elif cmd == 'set_user_group':
        if args is None:
            return jsonify({"error": "Missing args parameter."}), 400
        if isinstance(args.get("user_id"), int) and isinstance(args.get("group_id"), int):
            db.update_user_group(args.get("user_id"), args.get("group_id"))
            return jsonify({"message": "ok"})
        else:
            return jsonify({"error": "Need args user_id and group_id parameters to be integers."}), 200
    elif cmd == "delete_user":
        if args is None:
            return jsonify({"error": "Missing args parameter."}), 400
        if isinstance(args.get("user_id"), int):
            db.delete_user(args.get("user_id"))
            return jsonify({"message": "ok"})
    else:
        return jsonify({"error": "Unknown debug cmd."}), 400


def init():
    global config
    config['POSTGRES_HOST'] = os.environ.get('POSTGRES_HOST') if os.environ.get('POSTGRES_HOST') else 'localhost'
    config['POSTGRES_PORT'] = int(os.environ.get('POSTGRES_PORT')) if os.environ.get('POSTGRES_PORT') else 5432
    config['POSTGRES_USER'] = os.environ.get('POSTGRES_USER') if os.environ.get('POSTGRES_USER') else 'fs'
    config['POSTGRES_PASSWORD'] = os.environ.get('POSTGRES_PASSWORD') if os.environ.get(
        'POSTGRES_PASSWORD') else 'default'
    config['POSTGRES_DB'] = os.environ.get('POSTGRES_DB') if os.environ.get('POSTGRES_DB') else 'master'

    logging.basicConfig(level=logging.INFO)

    connections = db.init_db(config['POSTGRES_HOST'], config['POSTGRES_PORT'], config['POSTGRES_USER'], config['POSTGRES_PASSWORD'], config['POSTGRES_DB'])

    retry_limit = 10
    for _ in range(retry_limit):
        try:
            if connections:
                # Generate 50 users with mock data if no users are in the table
                users = db.get_all_users()

                if users is None:
                    test_user = generate_database_user()
                    test_user.email = 'test@uwaterloo.ca'
                    db.create_user(test_user, mock=True)
                    for i in range(49):
                        user = generate_database_user()
                        db.create_user(user, mock=True)
            break
        except:
            import traceback
            traceback.print_exc()
            logging.warn("Trying again in 1 second.")
            time.sleep(1)

    # Start matching cronjob
    matcher.init()


if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', threaded=True)
