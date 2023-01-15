
# temporary fix for integration issues
def convert_user_to_profile(user):
    return {
        "id": user['id'],
        "email": user['email'],
        "classYear": user['class_year'],
        "firstName": user['first_name'],
        "lastName": user['last_name'],
        "program": user['program'],
        "avatarURL": user['avatar_url'],
        "displayName": user['display_name'],
        "bio": user['bio'],
    }