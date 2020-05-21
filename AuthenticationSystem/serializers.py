from rest_framework import serializers
# from .models import UsersSignUp
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate

providers = [('facebook', 'Facebook'), ('google', 'Google'), ('email', 'Email')]


class SocialSerializer1(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email','password','remember_me')
    remember_me = serializers.BooleanField()



class SocialSerializer2(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)




class UsersSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password', 'email')

# class UsersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('password', 'email','remember_me')
#     # email = serializers.CharField()
#     # password = serializers.CharField()
#     # tdvalue = serializers.DecimalField(max_digits = 10000, decimal_places = 0)
#     remember_me = serializers.CharField()
#     def validate (self, data):
#         email = data.get("email", "")
#         password = data.get("password", "")

#         if username and password:
#             user = authenticate(username = email , password = password)
#             if user:
#                 if user.is_active:
#                     data["user"] = user
#                 else:
#                     msg = "Account is not Activated"
#                     return Response(msg, status = 400)

#             else:
#                 msg = "Unable to login using the given cridentials."
#                 return Response(msg, status = 400)
#         else:
#             msg = "Must provide username and password"
#             return Response(msg , status = 400)
#         return data


class UsersSignInSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password', 'email','remember_me')
    # username = serializers.CharField()
    # password = serializers.CharField()
    remember_me = serializers.CharField()


# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = ('name',)


# class SignUpAPI2Serializer(serializers.ModelSerializer):
#     groups = GroupSerializer(many=True)
#     class Meta:
#         model = User
#         fields = ('username','password','email','groups','first_name',)
#


# class SignUpAPISerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username','password','email','first_name',)


#     def create(self, validated_data):
#         user = User.objects.get_or_create(**validated_data)
#         password = validated_data.pop('password')
#         user.set_password(password)
#         user.save()
#         return user
