from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Profile, User
from AuthenticationSystem.models import Error
from .serializers import ProfileSerializer, EditProfileSerializer
import base64
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import get_authorization_header
import jwt
from RT_Website_19.settings import SECRET_KEY
from pinax.eventlog.models import log
import datetime

def log_errors(ex,id):
    now = datetime.datetime.now()
    user= User.objects.filter(id=id).first()
    error = Error(user= user,error=ex, time = now)
    error.save()


# The function is used to get the ID of the user who sent the token
# by decoding the Jwt. Parameter: the request, Returns: user ID
def get_user_ID(request):

    try:
        auth = get_authorization_header(request).split()
        token=auth[1]
        secret= SECRET_KEY # the secret key from the settings
        payload= jwt.decode(token,secret)
        return payload['user_id']
    except Exception as ex:
        return -1




class profile(APIView):

# This function returns a JSON that contains the profile data of the user
# that sent the request, it accepts GET requests
    def get(self, request):
        try:
            id =get_user_ID(request)
            if (id == -1):
                return Response("The jwt token isn't correct", status=status.HTTP_401_UNAUTHORIZED)
            # checks if the user doesn't have an account
            if(not(Profile.objects.filter(user=id).exists())):
                return Response("This user doesn't have a profile yet", status=status.HTTP_400_BAD_REQUEST)
            profiles= Profile.objects.filter(user=id)
            serializer= ProfileSerializer(profiles,many=True)
            # Stores "View Profile" activity in the database
            log(user=User.objects.filter(id=id).first(), action="Viewed Profile",)
            return Response(serializer.data)
        except Exception as ex:
            log_errors(str(ex),id)
            return Response("Please contact the fan page!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This function is used to create new profiles for registered users, it accepts POST requests
    def post(self, request):
        try:
            if(request.data["national_front"] =="" or request.data["national_back"] == ""):
                return Response("The national ID images can't be  blank", status=status.HTTP_400_BAD_REQUEST)
            # gets the ID of the user that sent the request
            id =get_user_ID(request)
            if (id == -1):
                return Response("The jwt token isn't correct", status=status.HTTP_401_UNAUTHORIZED)
            # checks if this user already has a profile
            if(Profile.objects.filter(user=id).exists()):
                return Response("This user already has a profile", status=status.HTTP_400_BAD_REQUEST)
            request.data['user']=id
            serializer = ProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                # Stores "Create Profile" activity in the database
                log(user=User.objects.filter(id=id).first(), action="Created Profile",)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            log(user=User.objects.filter(id=id).first(),action="Tried to Create Profile",)           
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            log_errors(str(ex),id)
            return Response("Please contact the fan page!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This class is used to edit the user's profile data. When accessed whith GET request it
# returns the profile data of the user who made the request. When accessed with POST request
# it gets the new data from the user to edit his profile
    def put(self, request):
        try:
            # gets the ID of the user that sent the request
            id =get_user_ID(request)
            if (id == -1):
                return Response("The jwt token isn't correct", status=status.HTTP_401_UNAUTHORIZED)
            # checks if the user doesn't have an account
            if(not (Profile.objects.filter(user=id).exists())):
                return Response("This user doesn't have a profile yet", status=status.HTTP_400_BAD_REQUEST)
            profiles=Profile.objects.filter(user=id).first()
            # checks if there are empty images
            if(request.data["national_front"]==""):
                request.data.pop('national_front',None)
            if(request.data["national_back"]==""):
                request.data.pop('national_back',None)
            if(request.data["profile_pic"]==""):
                request.data.pop('profile_pic',None)
            if(request.data["passport_img"]==""):
                request.data.pop('passport_img',None)
            serializer = EditProfileSerializer(profiles,data=request.data)
            if serializer.is_valid():
                serializer.save()
                # Stores "Edit Profile" activity in the database
                log(user=User.objects.filter(id=id).first(), action="Edited Profile",)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            log(user=User.objects.filter(id=id).first(),action="Tried to edit Profile",)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            log_errors(str(ex),id)
            return Response("Please contact the fan page!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
