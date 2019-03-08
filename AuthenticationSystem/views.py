from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UsersSignUpSerializer,UsersSerializer,SocialSerializer,UsersSignInSerializer
# from .serializers import UsersSignUpSerializer, ADMINSerializer
from rest_framework.parsers import JSONParser
import io
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import get_authorization_header
# from AdminPanel.settings import api_settings
import jwt
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate







# the the post function now contains a

class SignUpView(APIView):
    def post(self, request):
        serializer = UsersSignUpSerializer(data=request.data)
        if serializer.is_valid():
            defaultGroup = Group.objects.get(name='Waiting Verification')
            user = User.objects.create(username = serializer.validated_data['username'],email = serializer.validated_data['username'],)
            defaultGroup = Group.objects.get(name='Waiting Verification')
            user.set_password(serializer.validated_data['password'])
            defaultGroup.user_set.add(user)
            user.save()
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user, 'false')
            token = jwt_encode_handler(payload)
            return Response({"token": token}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# # ///////////////////////////////////////////////////////////////////////////////////////////////
#             # else:
#             #     try:
#             #         #check if the email entered as a social user email that already exist
#             #         SocialUsers.objects.get(user=User.objects.get(email=serializer.validated_data["email"]))
#             #     except SocialUsers.DoesNotExist:
#             #         #No IT DOESN'T EXIST AS A SOCIAL ACCOUNT , BUT IT EXISTS AS A NORMAL ACCOUNT
#             #         return Response({"error": "The Email Already Exists!"}, status=status.HTTP_401_UNAUTHORIZED)
#             #     else:
#             #         #YES IT EXISTS AS A SOCIAL ACCOUNT
#             #         return Response({"error": "The Email exist as a social account"},status=status.HTTP_401_UNAUTHORIZED)

#             # defaultGroup = Group.objects.get(name='Waiting Verification')
#             # user = User.objects.create(username = serializer.validated_data['username'],)
#             # user.set_password(serializer.validated_data['password'])
#             # defaultGroup.user_set.add(user)
#             # user.save()
#             # return Response(status=status.HTTP_201_CREATED)
#     # ///////////////////////////////////////////////////////////////////////////////////////////////

#         else :
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#ADMIN VIEW
class ADMIN(APIView):

    # @method_decorator(login_required(login_url='/signin'))

    def get(self,request):
        # id = get_user_ID(request)
        # if( not (UsersSignUp.objects.filter(username = id).exists())):
        #     return Response("This user doesn't have a profile yet", status=status.HTTP_400_BAD_REQUEST)

        Admin = User.objects.all()
        serializer = ADMINSerializer(Admin, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ADMINSerializer(data=request.data)
        if serializer.is_valid():
            RequiredUser = serializer.validated_data['username']
            GroupToSet = serializer.validated_data['group']
            # G = Group.objects.get(name = GroupToSet)
            user = User.objects.get(username = RequiredUser)
            # G.user_set.add(user)
            # user.groups.add(GroupToSet)
            GroupToSet.add(user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# sign in view that will contain by email

class SignInView(APIView):
    def post(self, request):
        serializer = UsersSignInSerializer(data=request.data)
        if serializer.is_valid():
            remember_me = serializer.validated_data["remember_me"]
            user = User.objects.get(username=serializer.validated_data["username"])
            authenticate(username=user.username,password=serializer.validated_data["password"])
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user, remember_me)
            token = jwt_encode_handler(payload)
            return Response({"token":token}, status = 200)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class SocialSignInView(APIView):

    def post(self, request):
        social_serializer = SocialSerializer(data=request.data)
        if social_serializer.is_valid():
            try:
                user = UsersSignUp.objects.get(username=social_serializer.validated_data["email"])
            except UsersSignUp.DoesNotExist:
                # return Response({"error": "Social account doesn't exist, Please sign up first"}, status=status.HTTP_401_UNAUTHORIZED)
                try:
                    user = UsersSignUp.objects.get(password=social_serializer.validated_data["socialID"])
                except UsersSignUp.DoesNotExist:
                    user = UsersSignUp.objects.create_user(username=social_serializer.validated_data["email"],password=social_serializer_email.validated_data["password"],proprovider=social_serializer_email.validated_data["provider"])
                    social_serializer.save(user=user)
                    my_group = Group.objects.get(name='NOT_VERIFIED')
                    my_group.user_set.add(user)
                else:
                    if social_serializer.validated_data["provider"] == user.provider:
                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                        payload = jwt_payload_handler(user.user)
                        token = jwt_encode_handler(payload)
                        return Response({"token": token}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"Error": "Social provider is wrong"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if social_serializer.validated_data["provider"] == user.provider:
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                    payload = jwt_payload_handler(user.user)
                    token = jwt_encode_handler(payload)
                    return Response({"token": token}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"Error": "Social provider is wrong"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(social_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Class that contain the apis for processing forget password issue.
# HTTP methods to interact : POST request in which the user issue a password reset request
class ForgetPasswordView(APIView):

    def post(self, request):
        try:
            #check that the email recieved successfully
            request.data["email"]
        except KeyError:
            return Response({"error": "some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            #check that a user with that email already exist
            user = UsersSignUp.objects.get(username=request.data["email"])
            if user.provider!="":
                return Response({"error": "Can't reset a social account password"}, status=status.HTTP_401_UNAUTHORIZED)
        except UsersSignUp.DoesNotExist:
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
            reset_password_link = "http://sys.asuracingteam.org/changePassword/" + token + "/"
            # prepare the email content to be sent.
            email_content = "Click on This link to Proceed:<br><br>" + "<a href="+reset_password_link+">Reset Password</a><br><br>ASU Racing Team"
            return sendRTMail(sender = settings.EMAIL_HOST_USER, receiverList = [user.email],subject ='Password Reset',content = email_content )

# Class that contain the apis to change password.
# HTTP methods to interact : POST request in which the password is to be actually changed
class ChangePasswordView(APIView):

    def post(self, request):
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
            user = UsersSignUp.objects.get(username=token_info["username"])
        except UsersSignUp.DoesNotExist:
            return Response({"error": "token is wrong"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user.set_password(request.data["password"])
            user.save()
        except Exception as e:
            return Response({"error": "Please try again later"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"done": "Password is Changed"},status=status.HTTP_200_OK)





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
#                 user = UsersSignUp.objects.get(username=serializer.validated_data["email"])
#             except UsersSignUp.DoesNotExist:
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
#                         UsersSignUp.objects.get(user=user)
#                     except UsersSignUp.DoesNotExist:
#                         #no , then there is something wrong with the data inserted.
#                         return Response({"Error": "Password provided is wrong","error": "Email/Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
#                     else:
#                         #yes exist as a social user , can't login
#                         return Response({"error": "The Email exist as a social account, login using your social account"},status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             #Invalid data inserted
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)