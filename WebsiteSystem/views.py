from django.shortcuts import render
from .models import Sponsor, Image, Team , Event, NewsFeed, FAQ , Highlight, Achievement
from .serializers import SponsorSerializer, EventSerializer, NewsFeedSerializer, ImageSerializer, FAQSerializer ,HighlightSerializer, TeamSerializer, GroupSerializer, AchievementSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.paginator import *
from django.contrib.auth.models import Group, User
from ProfileSystem.models import Profile
import jwt
from RT_Website_19.settings import SECRET_KEY
from rest_framework.authentication import get_authorization_header
from AuthenticationSystem.models import Error
from ProfileSystem.views import get_user_ID, log_errors
from pinax.eventlog.models import log
from django.core.exceptions import ObjectDoesNotExist


# A Function To Verify The Token Using The "jwt.decode" Function

def TokenVerify(request):
    try:
        try:
            auth = get_authorization_header(request).split()
            token=auth[1]
            secret= SECRET_KEY # the secret key from the settings
            jwt.decode(token , secret)
            return True
        except:
            return False
    except Exception as ex:
        log_errors(str(ex),id)
        return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

# A Function That Verifies If The User Has Permission To Edit The Data , The Position Condition Can Be Changed To The Required Group

def BackEndPermissionVerifier(request):
    auth = get_authorization_header(request).split()
    token=auth[1]
    secret= SECRET_KEY # the secret key from the settings
    payload = jwt.decode(token , secret)
    try:
        if payload['position'] == 'IT -SeniorOfficer' :
            return True
        else :
            return False
    except:
        log_errors(str(ex),id)
        return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)


# 0: to remove image form team
# 1: to remove achievement form team
# 2: to remove image form event
# 3: to remove image form highlight
# 4: to remove image form newsfeed
class RemoveFromView(APIView):
    def get(self, request, type,first_id, second_id):
        try:
            if TokenVerify(request) and BackEndPermissionVerifier(request) :
                if(type == 0):
                    Team.objects.get(id = first_id).image.remove(Image.objects.get(id = second_id))
                    Image.objects.get(id = second_id).delete()
                if(type == 1):
                    Team.objects.get(id = first_id).achievement.remove(Achievement.objects.get(id = second_id))
                    Achievement.objects.get(id = second_id).delete()
                if(type == 2):
                    Event.objects.get(id = first_id).image.remove(Image.objects.get(id = second_id))
                    Image.objects.get(id = second_id).delete()
                if(type == 3):
                    Highlight.objects.get(id = first_id).image.remove(Image.objects.get(id = second_id))
                    Image.objects.get(id = second_id).delete()
                if(type == 4):
                    NewsFeed.objects.get(id = first_id).image.remove(Image.objects.get(id = second_id))
                    Image.objects.get(id = second_id).delete()
                return Response("deleted", status=status.HTTP_201_CREATED)
            else:
                return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"msg":"An error has happened"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# A Class View That Return All The Sponsors

class SponsorGetView (APIView):
    #View all sponsors
    def get(self,request):
        try:
            #id =get_user_ID(request)
            sponsors= Sponsor.objects.all()
            serializer= SponsorSerializer(sponsors, many= True)
            log(user=User.objects.get(id=1), action="Viewed all sponsors",)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"msg":"An error has happened"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# A Class View That Add A Sponsor

class SponsorPostView (APIView):
    #Add a new sponsor
    def post(self, request): 
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                id =get_user_ID(request)
                serializer= SponsorSerializer(data= request.data)
                if serializer.is_valid():
                    serializer.save()
                    log(user=User.objects.get(id=id), action="Added a sponsor",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=id),action="Tried to add a sponsor",)
                    return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),id)
                return Response({"msg":"An error has happened"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Delete A Sponsor

class SponsorDelView (APIView):
    #Delete a sponsor 
    def delete(self, request,pk):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                if Sponsor.objects.get(id=pk):
                    Sponsor.objects.get(id=pk).delete()
                    log(user=User.objects.get(id=I), action="Deleted a sponsor",)
                    return Response({"msg":"Deleted successfully!"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"msg":"This sponsor doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Return All The Highlights

class AllHighlights (APIView):
    #Function to view all highlights using URL : /api/highlight/all/
    def get(self, request):
        try:
            #id =get_user_ID(request)
            Highlights = Highlight.objects.all()
            serializer = HighlightSerializer(Highlights, many = True)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# A Class View That Edit A Specific Highlight

class Highlights (APIView):
    def get(self, request,id):
        try:
            #I =get_user_ID(request)
            Highlights = Highlight.objects.get(id = id)
            serializer = HighlightSerializer(Highlights)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response("This highlight doesn't exist", status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #Function to edit an already existing highlight using URL : /api/highlight/
    def put(self ,request ,id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                image = {}
                highlights = Highlight.objects.get(id = id)
                image["image"]=request.data["image"]
                if(image["image"] != ""):
                    image=ImageSerializer(data= image)
                    if image.is_valid():
                        image.save()
                        highlights.image.add(Image.objects.last().id)
                    else:
                        return Response(image.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    request.data.pop('image',None)

                serializer= HighlightSerializer(highlights, data= request.data)
                if serializer.is_valid():
                    serializer.save()
                    log(user=User.objects.get(id=I), action="Updated a highlight",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=I), action="Tried to update a highlight",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"msg":"This highlight doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"Token Validation": "False"}, status=status.HTTP_400_BAD_REQUEST)
    #Function to delete a highlight using URL : /api/highlight/
    def delete (self, request, id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request) #get id
                Highlight.objects.get(id = id).delete()
                log(user=User.objects.get(id=I), action="Deleted a highlight",)
                return Response({"msg":"Deleted successfully"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"msg":"This highlight doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

    #Function to add a new highlight using URL : /api/highlight/

# A Class View That Adds A Higlight

class PostHighlight(APIView):
    def post(self, request):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                id =get_user_ID(request)
                image = {}
                image["image"]=request.data["image"]
                image = ImageSerializer(data = image)
                if image.is_valid():
                    image.save()
                else:
                    return Response(image.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer = HighlightSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.validated_data["image"]= [Image.objects.last().id]
                    serializer.save()
                    log(user=User.objects.get(id=id),action="Added a highlight",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=id),action="Tried to add a highlight",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),id)
                return Response({"msg":"Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # return Response({"Token Validation": "False"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

    
# A Class View That Return Only Active Highlights

class ActiveHighlights (APIView):
    #Function to get active Highlights using url : /api/highlight/active/
    def get(self, request):
        try:
            #id =get_user_ID(request)
            Highlights = Highlight.objects.filter(active = "True")
            serializer = HighlightSerializer(Highlights, many = True)
            return Response(serializer.data)
        except Exception as ex:

            # return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"msg":"Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# A Class View That Return All The Events

class AllEvents (APIView):
    #Function to view all events using URL : /api/events/all/
    def get(self, request):
        try:
            #id =get_user_ID(request)
            Events = Event.objects.all()
            serializer = EventSerializer(Events, many = True)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"msg":"Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# A Class View That Add Event

class PostEvent(APIView):
    #Function to add a new event using URL : /api/events/
    def post(self, request):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            #to be able to send images , we must first check if image is valid , then save that image , and we will then obtain it from the
            #image table
            try:
                id =get_user_ID(request)
                image = {}
                image["image"]=request.data["image"]
                image = ImageSerializer(data = image)
                if image.is_valid():
                    image.save()
                else:
                    return Response(image.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer = EventSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.validated_data["image"]= [Image.objects.last().id]
                    serializer.save()
                    log(user=User.objects.get(id=id),action="Added an event",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=id),action="Tried to add an event",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),id)
                return Response({"msg":"An error has happened!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Edit Event

class Events (APIView):
    def get(self, request, id):
        try:
            event = Event.objects.get(id= id)
            serializer = EventSerializer(event)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"msg":"This event doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #Function to edit an already existing event using URL : /api/events/
    def put(self ,request ,id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                image = {}
                Events = Event.objects.get(id = id)
                image["image"]=request.data["image"]
                if(image["image"] != ""):
                    image=ImageSerializer(data= image)
                    if image.is_valid():
                        image.save()
                        Events.image.add(Image.objects.last().id)
                    else:
                        return Response(image.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    request.data.pop('image',None)

                serializer= EventSerializer(Events, data= request.data)
                if serializer.is_valid():
                    serializer.save()
                    log(user=User.objects.get(id=I), action="Updated an event",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=I), action="Tried to update an event",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"msg":"This event doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

    #Function to delete an event using URL : /api/events/
    def delete(self , request ,id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                Event.objects.get(id = id).delete()
                log(user=User.objects.get(id=I), action="Deleted an event",)
                return Response({"msg":"Deleted successfully"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"msg":"This event doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Return Only Active Events

class ActiveEvents (APIView):
    #Function to get active events using url : /api/events/active/

    def get(self, request):
        try:
            #
            # id =get_user_ID(request)
            Events = Event.objects.filter(status = "True")
            serializer = EventSerializer(Events, many = True)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"msg":"Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# A Class View That Returns All Teams

class TeamView (APIView):
    #View all teams URL : /api/teams/
    def get (self,request):
        try:
            #id =get_user_ID(request)
            teams= Team.objects.all()
            serializer= TeamSerializer(teams, many= True)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #Add a new Team URL : /api/teams/
    def post (self, request):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                id =get_user_ID(request)
                serializer= TeamSerializer(data= request.data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    log(user=User.objects.get(id=id),action="Tried to add a team",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                teams = Team.objects.last()
                #achievement = {}  #name of the obj (JSON)-----DICTIONARY
                achievement=request.data["achievement"]  #field inside the dic , put data inside it key=value
                for single_achievement in achievement :
                    single_achievement = AchievementSerializer(data = single_achievement)
                    if single_achievement.is_valid():
                        single_achievement.save()
                        teams.achievement.add(Achievement.objects.last())
                    else:
                        return Response(single_achievement.errors, status=status.HTTP_400_BAD_REQUEST)
                image = request.data["image"]
                for single_image in image:
                    single_image = ImageSerializer(data = single_image)
                    if single_image.is_valid():
                        single_image.save()
                        teams.image.add(Image.objects.last())
                    else:
                        return Response(single_image.errors, status = status.HTTP_400_BAD_REQUEST)
                log(user=User.objects.get(id=id),action="Added a team",)
                return Response(serializer.data, status= status.HTTP_201_CREATED)
            except Exception as ex:
                    log_errors(str(ex),id)
                    return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else :
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Edit A Specific Team

class TeamEditView (APIView):
    #Edit a team URL : /api/teams/id
    def put (self, request, pk):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                teams = Team.objects.get(id = pk)
                achievements= request.data["achievement"]
                for single_achievement in achievements :
                    if(Achievement.objects.filter(id = single_achievement["id"]).exists()):
                        ach = Achievement.objects.get(id = single_achievement["id"])
                        if(single_achievement["image"]==""):
                            single_achievement.pop('image', None)
                        single_achievement = AchievementSerializer(ach,data = single_achievement)
                        if single_achievement.is_valid():
                            single_achievement.save()
                        else:
                            return Response(single_achievement.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        single_achievement = AchievementSerializer(data = single_achievement)
                        if single_achievement.is_valid():
                            single_achievement.save()
                            teams.achievement.add(Achievement.objects.last())
                        else:
                            return Response(single_achievement.errors, status=status.HTTP_400_BAD_REQUEST)

                images= request.data["image"]
                for i in teams.image.all():
                    teams.image.remove(i)
                    i.delete()
                for single_image in images :
                    single_image = ImageSerializer(data = single_image)
                    if single_image.is_valid():
                        single_image.save()
                        teams.image.add(Image.objects.last())
                    else:
                        return Response(single_image.errors, status=status.HTTP_400_BAD_REQUEST)


                serializer= TeamSerializer(teams, data= request.data)
                if serializer.is_valid():
                    serializer.save()
                    log(user=User.objects.get(id=I), action="Updated a team",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=I), action="Tried to update a team",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"msg":"This team doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),1)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
    #View a team by id URL : /api/teams/id
    def get (self,request,pk):
        try:
            #I =get_user_ID(request)
            if Team.objects.filter(id = pk).first():
                teams = Team.objects.filter(id = pk).first()
                serializer= TeamSerializer(teams)
                return Response(serializer.data)
            else:
                return Response({"msg" :"Team doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
                return Response({"msg":"This team doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    #Delete a team by id URL : /api/teams/id
    def delete (self, request, pk):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                teams = Team.objects.get(id=pk)
                for i in teams.achievement.all():
                    ach = Achievement.objects.get(id=i.id)
                    teams.achievement.remove(ach)
                    ach.delete()
                teams.delete()
                log(user=User.objects.get(id=I), action="Deleted a team",)
                return Response({"msg":"Deleted successfully!"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"msg":"This team doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Returns All News

class NewsFeedView(APIView):
    def get(self, request, page_number):
        try:
            #id =get_user_ID(request)
            data={}
            news = NewsFeed.objects.all().order_by('-date')
            news.reverse()
            pages = Paginator(news, 5)
            page = pages.page(page_number)
            serializer = NewsFeedSerializer(page, many= True)
            data["num_pages"]=pages.num_pages
            data["articles"]= serializer.data
            return Response(data)
        except EmptyPage :
            return Response({"msg":"This page doesn't exist "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as ex:
            return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# A Class View That Edits News

class EditNewsFeedView(APIView):
    def get(sef, request, id):
        try:
            news = NewsFeed.objects.get(id= id)
            serializer = NewsFeedSerializer(news)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"msg":"This news doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self,request, id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                image = {}
                news = NewsFeed.objects.get(id = id)
                image["image"]=request.data["image"]
                if(image["image"] != ""):
                    image=ImageSerializer(data= image)
                    if image.is_valid():
                        image.save()
                        news.image.add(Image.objects.last().id)
                    else:
                        return Response(image.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    request.data.pop('image',None)

                serializer= NewsFeedSerializer(news, data= request.data)
                if serializer.is_valid():
                    serializer.save()
                    log(user=User.objects.get(id=I), action="Updated a newsfeed",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=I), action="Tried to update newfeed",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"msg":"This news doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request, id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                news = NewsFeed.objects.get(id = id).delete()
                log(user=User.objects.get(id=I), action="Deleted a newsfeed",)
                return Response({"msg":"Deleted successfully"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"msg":"This news doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Adds News

class PostNewsFeedView(APIView):   
    def post(self, request):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                id =get_user_ID(request)
                image = {}
                image["image"]=request.data["image"]
                image = ImageSerializer(data = image)
                if image.is_valid():
                    image.save()
                else:
                    return Response(image.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer= NewsFeedSerializer(data= request.data)
                if serializer.is_valid():
                    serializer.validated_data["image"]= [Image.objects.last().id]
                    serializer.save()
                    log(user=User.objects.get(id=id),action="Added a newsfeed",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=id),action="Tried to add a newsfeed",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),id)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "Token Invalid"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Returns All FAQs

class FAQView(APIView):
    def get(self,request):
        try:
            #id =get_user_ID(request)
            Faqs=FAQ.objects.all()
            serializer = FAQSerializer(Faqs, many= True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"msg":"An error has happened!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        if TokenVerify(request) :
            try:
                id =get_user_ID(request)
                serializer = FAQSerializer(data=request.data)
                if (serializer.is_valid()):
                    serializer.save()
                    log(user=User.objects.get(id=id),action="Added FAQ",)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    log(user=User.objects.get(id=id),action="Tried to add FAQ",)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),id)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else :
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Deletes A Specific FAQ

class DeleteFaqView(APIView):
    def delete(self,request,id):
        if TokenVerify(request) :
            try:
                I =get_user_ID(request)
                FAQ.objects.get(id = id).delete()
                log(user=User.objects.get(id=I), action="Deleted a FAQ",)
                return Response({"msg":"Deleted successfully"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"msg":"This FAQ doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Returns All Users

class AllUsers(APIView):
    def get(self,request):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                profiles = Profile.objects.all()
                user_list = []
                for i in profiles:
                    user_dictionary = {} #key + value
                    user_dictionary ["id"] = i.user.id
                    user_dictionary ["email"] = i.user.email
                    user_dictionary ["name"] = i.name
                    user_dictionary ["phone"] = i.mobile
                    user_dictionary ["college_id"] = i.college_id
                    user_dictionary ["group"] = i.user.groups.all().first().name
                    user_list.append(user_dictionary)
                return Response(user_list)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Edits Specific User

class UserView(APIView):
    def get(self,request,id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I =get_user_ID(request)
                # TargetUser = User.objects.filter(id = id).first()
                profile = Profile.objects.get(user = id)
                user_dictionary = {}
                user_dictionary["name"] = profile.name
                user_dictionary["phone"] = profile.mobile
                user_dictionary["college_id"] = profile.college_id
                user_dictionary["email"] = profile.user.email
                user_dictionary["group"] = profile.user.groups.all().first().name
                log(user=User.objects.get(id=I), action="Viewed one user",)
                return Response(user_dictionary)
            except ObjectDoesNotExist:
                return Response({"msg":"This user doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,id):
        if TokenVerify(request) and BackEndPermissionVerifier(request) :
            try:
                I = get_user_ID(request)
                user = User.objects.get(pk = id)
                updated_group = Group.objects.get(name = request.data['group'])
                print(user)
                user.groups.clear()
                user.groups.add(updated_group)
                log(user=User.objects.filter(id=I).first(), action="Updated a user",)
                return Response({"msg":"User Group Permissions SUccessfully Updated"} , status=status.HTTP_202_ACCEPTED)
            except ObjectDoesNotExist:
                return Response({"msg":"This user doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                log_errors(str(ex),I)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)

# A Class View That Returns All Groups

class GroupsView(APIView):
    def get(self,request):
        if TokenVerify(request):
            try:
                id =get_user_ID(request)
                groups = Group.objects.all()
                serializer = GroupSerializer(groups, many= True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as ex:
                log_errors(str(ex),id)
                return Response({"msg":"An error has happened! "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"msg": "unauthorized"}, status=status.HTTP_400_BAD_REQUEST)
            