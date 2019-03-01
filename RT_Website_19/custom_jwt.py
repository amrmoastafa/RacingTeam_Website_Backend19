# import jwt
# import uuid
# import warnings

# from calendar import timegm
# import datetime as date

# from datetime import datetime

# from rest_framework_jwt.compat import get_username
# from rest_framework_jwt.compat import get_username_field
# from rest_framework_jwt.settings import api_settings
# from AuthSystem.serializers import GroupSerializer
# import json
# from ProfileSystem.models import Profile


# def jwt_payload_handler(user, stay_logged_in):
#     username_field = get_username_field()
#     username = get_username(user)

#     warnings.warn(
#         'The following fields will be removed in the future: '
#         '`email` and `user_id`. ',
#         DeprecationWarning
#     )

#     if stay_logged_in == 1:
#         expiry_date = datetime.utcnow() + date.timedelta(days=30)  # User's tokens will expiry on new year's day
#     elif stay_logged_in == 0:  # Tokens will expiry after the default expiration time has passed.
#         expiry_date = datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
#     else:
#         expiry_date = datetime.utcnow() + date.timedelta(hours=2)

#     try:
#         position=user.groups.all()[0].name
#     except IndexError:
#         position = "NOT_VERIFIED"
#     try:
#         prof=Profile.objects.get(user__pk=user.pk)
#         first_name = prof.firstName
#         if prof.profilePic:

#             profilePic = prof.profilePic.url
#         else:
#             profilePic = ''
            
#     except Profile.DoesNotExist:
#         profilePic = 'http://sys.asuracingteam.org/media/media/ProfileSystem/profile_pictures/88555f84-433.jpg'
#         first_name = ''
    
#     payload = {
#         'user_id': user.pk,
#         'username': username,
#         'exp': expiry_date,
#         'position': position,
#         'name': first_name,
#         'pic':profilePic
#     }


#     if hasattr(user, 'email'):
#         payload['email'] = user.email
#     if isinstance(user.pk, uuid.UUID):
#         payload['user_id'] = str(user.pk)

#     payload[username_field] = username

#     # Include original issued at time for a brand new token,
#     # to allow token refresh
#     if api_settings.JWT_ALLOW_REFRESH:
#         payload['orig_iat'] = timegm(
#             datetime.utcnow().utctimetuple()
#         )

#     if api_settings.JWT_AUDIENCE is not None:
#         payload['aud'] = api_settings.JWT_AUDIENCE

#     if api_settings.JWT_ISSUER is not None:
#         payload['iss'] = api_settings.JWT_ISSUER

#     # print(groupsRecieved.data[0])
#     # payload['position']=groupsRecieved[0]['name']

#     return payload
