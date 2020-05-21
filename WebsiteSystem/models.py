from django.db import models

class Image(models.Model):
    image = models.FileField()

class Highlight(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=15000)
    url= models.URLField()
    active= models.BooleanField()
    image = models.ManyToManyField(Image)

class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=15000)
    date = models.DateField()
    status= models.BooleanField()
    event_type = models.CharField(max_length=100)
    image = models.ManyToManyField(Image)

class NewsFeed(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=15000)
    date = models.DateField()
    status= models.BooleanField()
    article_type = models.CharField(max_length=100)
    video = models.URLField(default="", blank=True)
    image = models.ManyToManyField(Image)

class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=15000)
    year = models.DateField()
    position = models.CharField(max_length=50)
    image = models.FileField()


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=15000)
    team_type= models.CharField(max_length=100)
    image = models.ManyToManyField(Image)
    achievement = models.ManyToManyField(Achievement)


class Sponsor(models.Model):
    url=models.URLField()
    image = models.FileField()

class FAQ(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)