from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UsersSignUp
from .serializers import UsersSignUpSerializer,UsersSerializer,SocialSerializer1,SocialSerializer2
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





# the the post function now contains a
class SignUpList(APIView):
    def post(self, request):
        serializer = UsersSignUpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                #stayLoggedin value doesn't exist in the user model provided by Django so it is checked here for the token generation
                request.data["stayLoggedIn"]
            except KeyError:
                return Response({"error": "Some data is missing"}, status=status.HTTP_400_BAD_REQUEST)

            #needs change , swap try and except body , remove email field
            try:
                UsersSignUp.objects.get(email=serializer.validated_data["email"])
            except User.objects.filter(username = serializer.validated_data["email"]).DoesNotExist:
                try:
                    user = User.objects.create_user(username=serializer.validated_data["email"],email=serializer.validated_data["email"],password=serializer.validated_data["password"])
                    my_group = Group.objects.get(name='Waiting Verification')
                    my_group.user_set.add(user)
                except Exception:
                    Response({"error": "Please try again later"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                #generate token for the created User to have access to the RT website.
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(user, request.data["stayLoggedIn"])
                token = jwt_encode_handler(payload)
                # email verification is missing (To be Done in next years)
                return Response({"token": token}, status=status.HTTP_201_CREATED)
# ///////////////////////////////////////////////////////////////////////////////////////////////
            # else:
            #     try:
            #         #check if the email entered as a social user email that already exist
            #         SocialUsers.objects.get(user=User.objects.get(email=serializer.validated_data["email"]))
            #     except SocialUsers.DoesNotExist:
            #         #No IT DOESN'T EXIST AS A SOCIAL ACCOUNT , BUT IT EXISTS AS A NORMAL ACCOUNT
            #         return Response({"error": "The Email Already Exists!"}, status=status.HTTP_401_UNAUTHORIZED)
            #     else:
            #         #YES IT EXISTS AS A SOCIAL ACCOUNT
            #         return Response({"error": "The Email exist as a social account"},status=status.HTTP_401_UNAUTHORIZED)

            # defaultGroup = Group.objects.get(name='Waiting Verification')
            # user = User.objects.create(username = serializer.validated_data['username'],)
            # user.set_password(serializer.validated_data['password'])
            # defaultGroup.user_set.add(user)
            # user.save()
            # return Response(status=status.HTTP_201_CREATED)
    # ///////////////////////////////////////////////////////////////////////////////////////////////

        else :
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class EmailSignInView(APIView):

    def post(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.validated_data["email"]
                serializer.validated_data["password"]
                serializer.validated_data["remember_me"]
            except KeyError:
                return Response({"error": "Some data is missing"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = UsersSignUp.objects.get(username=serializer.validated_data["email"])
            except UsersSignUp.DoesNotExist:
                return Response({"Error": "Please Sign up first","error": "Email/Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                #sign in to the system
                if authenticate(username=user.username,password=serializer.validated_data["password"]):
                    #Generate the user JWT and return it to the front to be logged in
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                    payload = jwt_payload_handler(user, request.data["remember_me"])
                    token = jwt_encode_handler(payload)
                    return Response({"token": token}, status=status.HTTP_201_CREATED)
                else:
                    #not a normal user , then check the social user table
                    try:
                        UsersSignUp.objects.get(user=user)
                    except UsersSignUp.DoesNotExist:
                        #no , then there is something wrong with the data inserted.
                        return Response({"Error": "Password provided is wrong","error": "Email/Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        #yes exist as a social user , can't login
                        return Response({"error": "The Email exist as a social account, login using your social account"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            #Invalid data inserted
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        return Response({"success": "you are in login"}, status=status.HTTP_201_CREATED)



class Social(APIView):
    def post(self, request):
        serializer = SocialSerializer1(data=request.data)
        social_serializer_username = SocialSerializer2(data=request.data)
        if serializer.is_valid() and social_serializer_username.is_valid() :
            #new user
            try:
                social_serializer_username.validated_data["username"]
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


    def get(self, request):
        return Response(status=status.HTTP_200_OK)


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
