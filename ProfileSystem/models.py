from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    name =models.CharField(max_length=50, default="")
    mobile= models.CharField(max_length=15, unique=True)
    profile_pic= models.FileField(upload_to='pics')
    birth_date= models.DateField()
    address= models.CharField(max_length=200)
    university= models.CharField(max_length=100)
    faculty= models.CharField(max_length=100)
    college_department= models.CharField(max_length=100)
    graduation_year= models.IntegerField()
    college_id= models.CharField(max_length=15, default='', unique=True)
    emergency_name= models.CharField(max_length=50)
    emergency_mobile= models.CharField(max_length=15)
    emergency_relation= models.CharField(max_length=50)
    national_id= models.CharField(max_length=14, unique=True)
    national_front= models.FileField(upload_to='pics')
    national_back= models.FileField(upload_to='pics', blank=False)
    passport_id= models.CharField(max_length=9, blank=True, default='', unique=True)
    passport_img= models.FileField(upload_to='pics')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)

# class Error(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, default = 1)
#     error= models.CharField(max_length=500)
#     time= models.DateTimeField()



