import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from entities.user import UserUpdate
from entities.group import DatabaseGroup
from util import generate_database_user
import db
import re

app = Flask(__name__)
CORS(app)
config = {}


@app.route('/')
def hello_world():  # put application's code here
    return {
        "message": "FirstStep API v1"
    }


@app.post('/user')
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
def get_user():
    email = request.args.get("email")
    user = db.get_user(email)
    return jsonify(user), 200


@app.post('/user/profile')
def update_user():
    data = request.get_json()
    json_body = data["newProfile"]
    user = UserUpdate(
        id=json_body["id"],
        email=json_body["email"],
        class_year=json_body["classYear"],
        first_name=json_body["firstName"],
        last_name=json_body["lastName"],
        program_id=json_body["program"]["id"],
        avatar_url=json_body["avatarURL"],
        display_name=json_body["displayName"],
        bio=json_body["bio"]
    )
    db.update_user(user)
    return '', 204


@app.get('/user/skillsets')
def get_user_skillsets():
    user_id = request.args.get("userId")
    data = db.get_user_skillsets(user_id)
    return jsonify(data), 200


@app.get('/user/preferences')
def get_user_preferences():
    user_id = request.args.get("userId")
    data = db.get_user_preferences(user_id)
    return jsonify(data), 200


@app.post('/user/skillsets')
def update_user_skillsets():
    data = request.get_json()
    user_id = data["userId"]
    skillsets = data["newSkillsets"]
    db.update_user_skills(user_id, skillsets)
    return '', 204


@app.post('/user/preferences')
def update_user_preferences():
    data = request.get_json()
    user_id = data["userId"]
    preferences = data["newPreferences"]
    db.update_user_preferences(user_id, preferences)
    return '', 204


@app.post('/user/matching/join')
def update_user_matching_join():
    data = request.get_json()
    user_id = data["userId"]
    match_round_id = data["matchRoundId"]
    data = db.add_user_to_matching_round(user_id, match_round_id)
    return jsonify(data), 200


@app.post('/user/matching/leave')
def update_user_matching_leave():
    data = request.get_json()
    user_id = data["userId"]
    match_round_id = data["matchRoundId"]
    db.remove_user_from_matching_round(user_id, match_round_id)
    return '', 204


@app.delete('/user/profile')
def delete_user():
    user_id = request.args.get("userId")
    db.delete_user(user_id)
    return jsonify({"deleted": True}), 200


@app.post('/group')
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
def get_group():
    group_id = request.args.get("groupId")
    response = db.get_group(group_id)
    return jsonify(response), 200


@app.post('/group/profile')
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
def update_members():
    data = request.get_json()
    group_id = data["id"]
    members = data["members"]
    db.update_members(group_id, members)
    return '', 204


@app.post('/group/matching')
def group_commitment():
    data = request.get_json()
    commitment = False if data["action"] == 0 else True
    db.group_commitment(data["userId"], data["groupId"], commitment)
    return '', 204


@app.post('/group/commitment')
def commit_group():
    data = request.get_json()
    db.commit_group(data["groupId"], data["commit"])
    return '', 204


@app.delete('/group/profile')
def delete_group():
    group_id = request.args.get("groupId")
    db.delete_group(group_id)
    return jsonify({"deleted": True}), 200


@app.get('/global/matching/current')
def get_matching_round():
    data = db.get_matching_rounds()
    return jsonify(data), 200


@app.get('/global/skillsets/all')
def get_all_skillsets():
    data = db.get_all_skillsets()
    return jsonify(data), 200


@app.get('/global/preferences/all')
def get_all_preferences():
    data = db.get_all_preferences()
    return jsonify(data), 200


@app.get('/global/programs/all')
def get_all_programs():
    data = db.get_all_programs()
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
    db.init_db(config['POSTGRES_HOST'], config['POSTGRES_PORT'], config['POSTGRES_USER'], config['POSTGRES_PASSWORD'],
               config['POSTGRES_DB'])

    # Generate 50 users with mock data if no users are in the table
    users = db.get_all_users()
    if users is None:
        for i in range(50):
            user = generate_database_user()
            db.create_user(user)


if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', threaded=True)
