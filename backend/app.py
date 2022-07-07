from flask import Flask
from util import generate_test_user

app = Flask(__name__)

#f.write(json.dumps(obj, default=lambda x: x.__dict__, indent=4)) to write a json object

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.post('/user')
def create_user():
    #TODO create user and return new user id
    return generate_test_user()

@app.get('/user/<int:user_id>/profile')
def get_user_profile(user_id):
    #TODO: get user from schema
    return user_id

@app.get('/user/<int:user_id>/profile')
def post_user_profile(user_id):
    #TODO: update user from request
    return user_id

@app.get('/group/<int:group_id>')
def get_group(group_id):
    return id:

@app.post('/group/<int:group_id>/disband')
def disband_group(group_id):
    #Return status of group being deleted
    #TODO: disband group
    return True

@app.post('/group/<int:group_id>/commit')
def commit_group(group_id):
    #Return status of group being created
    #TODO: commit group
    return True

@app.get('/matching')
def get_matching():
    user_id = request.args.get('userid')
    return user_id

@app.post('/matching')
def post_matching():
    #TODO: update matching data from request
    return 0

@app.get('/skillsets/all')
def get_all_skillsets():
    return ""

@app.get('/preferences/all')
def get_all_preferences():
    return ""

if __name__ == '__main__':
    app.run()
