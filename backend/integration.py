
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

def reformat_user_payload(user):
    user_profile = convert_user_to_profile(user)
    user["profile"] = user_profile
    additionals = user["onboarding"]
    user["onboardingStatus"] = additionals["onboarding_status"]
    user["isVerified"] = additionals["is_verified"]
    user["isEligible"] = additionals["is_eligible"]
    user['has_group'] = True if (user['group_id']) else False
    return user
    
def reformat_user_skills(rows):
    formatted_rows = list(map(lambda r: { 'attributeId': r['skill_id'], 'data': r['rating'] }, rows))
    return formatted_rows

def reformat_user_preferences(rows):
    formatted_rows = list(map(lambda r: { 'attributeId': r['preference_id'], 'data': r['preferred'] }, rows))
    return formatted_rows

def reformat_join_matchround_resp(user_id, data):
    return {
        "userId": user_id,
        "matchroundId": data['id'],
        'success': True,
        'currentMatchround': data,
    }
