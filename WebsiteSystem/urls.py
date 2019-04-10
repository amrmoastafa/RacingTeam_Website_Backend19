from django.urls import path
from WebsiteSystem import views
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('sponsors/all/', views.SponsorGetView.as_view()),
    path('sponsors/', views.SponsorPostView.as_view()),
    path('sponsors/(?P<pk>[0-9]+)/$', views.SponsorDelView.as_view()),
    path('teams/',views.TeamView.as_view()),
    path('teams/(?P<pk>[0-9]+)/$',views.TeamEditView.as_view()),
    path('news-feed/<int:page_number>/',views.NewsFeedView.as_view()),
    path('edit-news-feed/<int:id>/',views.EditNewsFeedView.as_view()),
    path('news-feed/',views.PostNewsFeedView.as_view()),
    path('faq/',views.FAQView.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)