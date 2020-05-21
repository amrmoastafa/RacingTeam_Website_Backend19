from django.conf.urls import url
from ProfileSystem import views
from django.urls import path


urlpatterns = [
    path('', views.profile.as_view()),

]