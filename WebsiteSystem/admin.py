from django.contrib import admin
from .models import Team, Highlight, Event, Sponsor, Achievement, Image, FAQ, NewsFeed

admin.site.register([Team, Highlight, Event, Sponsor, Achievement, Image, FAQ, NewsFeed])
