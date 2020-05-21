from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UsersSignUpSerializer,UsersSignInSerializer,SocialSerializer1,SocialSerializer2
from rest_framework.parsers import JSONParser
import io
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import get_authorization_header
import jwt
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
import random,string
from .models import Error
import datetime


def log_errors(ex,id):
    now = datetime.datetime.now()
    user=User.objects.filter(id=id).first()
    error = Error(user = user , error = ex , time = now)
    error.save()


def password_generator(length = 8, chars=string.ascii_letters + '@%_' ):
    return ''.join(random.choice(chars) for _ in range(length))

class SignUpView(APIView):
    def post(self, request):
        try:
            serializer = UsersSignUpSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    serializer.validated_data["email"]
                    serializer.validated_data["password"]
                except KeyError:
                    return Response({"error": "Some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    User.objects.get(username=serializer.validated_data["email"])
                except User.DoesNotExist:
                    try:
                        user = User.objects.create_user(username = serializer.validated_data['email'],email = serializer.validated_data['email'])
                        defaultGroup = Group.objects.get(name='Waiting Verification')
                        user.set_password(serializer.validated_data['password'])
                        defaultGroup.user_set.add(user)
                        user.save()
                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                        payload = jwt_payload_handler(user, 'false')
                        token = jwt_encode_handler(payload)
                        return Response({"token": token}, status=status.HTTP_201_CREATED)
                    except:
                        return Response({"error": "Please try again later"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return Response({"error": "User exists before."}, status=status.HTTP_406_NOT_ACCEPTABLE)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            log_errors(str(ex),1)
            return Response("An error has happened!", status = status.HTTP_500_INTERNAL_SERVER_ERROR)

# sign in view that will contain by email

class SignInView(APIView):
    def post(self, request):
        try:
            serializer = UsersSignInSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    serializer.validated_data["email"]
                    serializer.validated_data["password"]
                    serializer.validated_data["remember_me"]
                except KeyError:
                    return Response({"error": "Some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    user = User.objects.get(username=serializer.validated_data["email"])
                except User.DoesNotExist:
                    return Response({"Error": "Please Sign up first","error": "Email/Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if authenticate(username=user.username,password=serializer.validated_data["password"]):
                        remember_me = serializer.validated_data["remember_me"]
                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                        payload = jwt_payload_handler(user, remember_me)
                        token = jwt_encode_handler(payload)
                        return Response({"token": token}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"Error": "Password provided is wrong","error": "Email/Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            log_errors(str(ex),1)
            return Response("An error has happened!", status = status.HTTP_500_INTERNAL_SERVER_ERROR)
#user exist view that checks if the email is already used
class UserExist(APIView):
    def get(self, request):
        try:
            serializer = UsersSignInSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    if User.objects.get(username=serializer.validated_data["username"]):
                        return Response({"exists":"true"}, status = status.HTTP_200_OK)
                except:
                    return Response({"exists":"false"}, status = status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            log_errors(str(ex),1)
            return Response("An error has happened!", status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class SocialAuthView(APIView):
    def post(self, request):
        try:    
            if 'provider' in request.data and 'email' in request.data and 'social_id' in request.data:
                try:
                    user = User.objects.get(email=request.data['email'])
                except User.DoesNotExist:
                    # Create new account with social data
                    user = User.objects.create_user(username=(request.data['provider'] + '-' + request.data['social_id']),email=request.data["email"],password= password_generator(length=8) )
                    my_group = Group.objects.get(name='Waiting Verification')
                    my_group.user_set.add(user)
                else:
                    if user.username == user.email:
                        #Not a social account
                        return Response({"error": "The Email exist as a normal account, Please Login with your email and password"},status=status.HTTP_401_UNAUTHORIZED)

                #Social account registered before
                username_temp = user.username
                provider,socialid = username_temp.split('-')
                if provider != request.data['provider'] and socialid != request.data['social_id'] :
                    return Response({'error':'Some Data Missing'}, status=status.HTTP_400_BAD_REQUEST)
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(user, 'false')
                token = jwt_encode_handler(payload)
                return Response({"token": token}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error':'Some Data Missing'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            log_errors(str(ex),1)
            return Response("An error has happened!", status = status.HTTP_500_INTERNAL_SERVER_ERROR)




# Class that contain the apis to change password.
# HTTP methods to interact : POST request in which the password is to be actually changed





class Social(APIView):
    def post(self, request):
        try:
            serializer = SocialSerializer1(data=request.data)
            social_serializer_username = SocialSerializer2(data=request.data)
            if serializer.is_valid() and social_serializer_username.is_valid() :
                #new user
                try:
                    social_serializer_username.validated_data["email"]
                except KeyError:
                    return Response({"error": "Some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    #1)checking whether the account already exists as a SOCIAL USER or not ?
                    user = User.objects.get(password=serializer.validated_data["password"])
                except Exception as e:
                    #1.1)No it doesn't exist as a socialUser , then check the normal user table
                    try:
                        user = User.objects.get(username=social_serializer_username.validated_data["username"])
                    except User.DoesNotExist:
                        try:
                            #1.1.1) not Found in any of the 2 tables (SocialUsers and User), then add this Social Account
                            user = User.objects.create_user(username=social_serializer_username.data['username'],password=serializer.validated_data['password'],email=serializer.validated_data['email'])
                            serializer.save()
                            # return Response(status=status.HTTP_200_OK)
                            my_group = Group.objects.get(name='Default')
                            my_group.user_set.add(user)
                        except Exception as e:
                            print(e)
                            # return Response({"error": "Please try again later","content":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                        payload = jwt_payload_handler(user, serializer.validated_data["remember_me"])
                        token = jwt_encode_handler(payload)
                        return Response({"token": token}, status=status.HTTP_201_CREATED)
                    else:
                        #1.1.2) exists as a normal user account, so won't be created again
                        return Response({"error": "The Account Already Exists, you should login using your Email"},status=status.HTTP_401_UNAUTHORIZED)
                else:
                    #1.2)YES that account already exist so, won't created again.
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                    payload = jwt_payload_handler(user.user, serializer.validated_data["remember_me"])
                    token = jwt_encode_handler(payload)
                    return Response({"token": token}, status=status.HTTP_201_CREATED)

            elif serializer.is_valid() and not social_serializer_username.is_valid():
                #existing user
                try:
                    user = User.objects.get(password=serializer.validated_data["password"])
                except User.DoesNotExist:
                    print("error")
                    # return Response({"error": "Social account doesn't exist, Please sign up first"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if serializer.validated_data["email"] == user.email:
                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                        payload = jwt_payload_handler(user.user, serializer.validated_data["remember_me"])
                        token = jwt_encode_handler(payload)
                        return Response({"token": token}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"Error": "Social provider is wrong"}, status=status.HTTP_401_UNAUTHORIZED)

            else:
                # wrong data
                #collect errors in data submitted to be sent to client side.
                social_serializer_username.is_valid()
                serializer.is_valid()
                errors = serializer.errors
                errors.update(social_serializer_username.errors)
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            log_errors(str(ex),1)
            return Response("An error has happened!", status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


# Class that contain the apis for processing forget password issue.
# HTTP methods to interact : POST request in which the user issue a password reset request
class ForgetPasswordView(APIView):

    def post(self, request):
        try:
            try:
                #check that the email recieved successfully
                request.data["email"]
            except KeyError:
                return Response({"error": "some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                #check that a user with that email already exist
                user = User.objects.get(username=request.data["email"])
                if user.email!=user.username:
                    return Response({"error": "Can't reset a social account password"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"error": "Email doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
            # try:
            #     #check that the email inserted is not a social account email.
            #     # IF that line " SocialUsers.objects.get(user=user) " execute successfully , then there is a social account for this email
            #     # and that we can't do anything about it's password.
            #     # ELSE it triggers DoesNotExist Exception that is to be handled below
            #     user = User.objects.get(user=user)
            #     return Response({"error": "Can't reset a social account password"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # At this point, we are sure that this email belongs to a normal account
                # generate token to login
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(user, 2)
                token = jwt_encode_handler(payload)
                # prepare the link to be sent in order for the user to use to change the password
                reset_password_link = "http://http://localhost:4200/auth/change-password/" + token + "/"
                # prepare the email content to be sent.
                email_content = "Click on This link to Proceed:<br><br>" + "<a href="+reset_password_link+">Reset Password</a><br><br>ASU Racing Team"
                return Response({"success": "Email sent: " + reset_password_link}, status=status.HTTP_200_OK)
                # return sendRTMail(sender = settings.EMAIL_HOST_USER, receiverList = [user.email],subject ='Password Reset',content = email_content )
        except Exception as ex:
            log_errors(str(ex),1)
            return Response("An error has happened!", status = status.HTTP_500_INTERNAL_SERVER_ERROR)
# Class that contain the apis to change password.
# HTTP methods to interact : POST request in which the password is to be actually changed
class ChangePasswordView(APIView):

    def post(self, request):
        try:
            try:
                request.data["token"]
                request.data["password"]
            except KeyError:
                return Response({"error": "Some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
            token = request.data["token"]
            jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
            try:
                token_info = jwt_decode_handler(token)
            except:
                return Response({"error": "Token Expired"}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                user = User.objects.get(username=token_info["username"])
            except User.DoesNotExist:
                return Response({"error": "token is wrong"}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                user.set_password(request.data["password"])
                user.save()
            except Exception as e:
                return Response({"error": "Please try again later"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            return Response({"done": "Password is Changed"},status=status.HTTP_200_OK)
        except Exception as ex:
            log_errors(str(ex),1)
            return Response("An error has happened!", status = status.HTTP_500_INTERNAL_SERVER_ERROR)




# class EmailSignInView(APIView):

#     def post(self, request):
#         serializer = UsersSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 serializer.validated_data["email"]
#                 serializer.validated_data["password"]
#                 serializer.validated_data["remember_me"]
#             except KeyError:
#                 return Response({"error": "Some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 user = User.objects.get(username=serializer.validated_data["email"])
#             except User.DoesNotExist:
#                 return Response({"Error": "Please Sign up first","error": "Email/Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 #sign in to the system
#                 if authenticate(username=user.username,password=serializer.validated_data["password"]):
#                     #Generate the user JWT and return it to the front to be logged in
#                     jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#                     jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#                     payload = jwt_payload_handler(user, request.data["remember_me"])
#                     token = jwt_encode_handler(payload)
#                     return Response({"token": token}, status=status.HTTP_201_CREATED)
#                 else:
#                     #not a normal user , then check the social user table
#                     try:
#                         User.objects.get(user=user)
#                     except User.DoesNotExist:
#                         #no , then there is something wrong with the data inserted.
#                         return Response({"Error": "Password provided is wrong","error": "Email/Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
#                     else:
#                         #yes exist as a social user , can't login
#                         return Response({"error": "The Email exist as a social account, login using your social account"},status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             #Invalid data inserted
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
