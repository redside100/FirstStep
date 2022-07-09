from flask import Flask, request, jsonify
from util import generate_test_user, create_groups

app = Flask(__name__)

#f.write(json.dumps(obj, default=lambda x: x.__dict__, indent=4)) to write a json object

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.post('/user')
def create_user():
    #TODO create user and return new user id
    user = request.get_json()
    return '', 204

@app.get('/user/<int:user_id>/profile')
def get_user_profile(user_id):
    #TODO: get user from schema
    return jsonify(generate_test_user()), 200

@app.post('/user/<int:user_id>/profile')
def post_user_profile(user_id):
    #TODO: update user from request
    return "updated user", 204

@app.get('/group/<int:group_id>')
def get_group(group_id):
    users = []
    for i in range(4):
        users.append(generate_test_user())
    group = create_groups(users, 4)
    return jsonify(group), 200

@app.post('/group/<int:group_id>/disband')
def disband_group(group_id):
    #Return status of group being deleted
    #TODO: disband group
    return '', 204

@app.post('/group/<int:group_id>/commit')
def commit_group(group_id):
    #Return status of group being created
    #TODO: commit group
    return '', 204

@app.get('/matching/status')
def get_matching():
    user_id = request.args.get('userid')
    return {"matching": "true"}, 200

@app.post('/matching')
def post_matching():
    #TODO: update matching data from request
    return '', 204

@app.get('/skillsets/all')
def get_all_skillsets():
    return {"leadership" : "1", "communication": "3"}, 200

@app.get('/preferences/all')
def get_all_preferences():
    return {"preferences": { "hardware": "true", "embedded systems": "true"}}, 200

if __name__ == '__main__':
    app.run()
