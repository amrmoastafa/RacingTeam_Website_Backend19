from rest_framework import serializers
from RT_Website_19.fields import Base64FileField
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    profile_pic = Base64FileField(max_length=None, use_url=True)
    national_front = Base64FileField(max_length=None, use_url=True, required= True)
    national_back = Base64FileField(max_length=None, use_url=True, required= True) 
    passport_img = Base64FileField(max_length=None, use_url=True)

    class Meta:
        model = Profile
        fields = '__all__'


class EditProfileSerializer(serializers.ModelSerializer):
    profile_pic = Base64FileField(max_length=None, use_url=True, required= False)
    national_front = Base64FileField(max_length=None, use_url=True, required= False)
    national_back = Base64FileField(max_length=None, use_url=True, required= False) 
    passport_img = Base64FileField(max_length=None, use_url=True, required= False)


    class Meta:
        model = Profile
        fields = '__all__'