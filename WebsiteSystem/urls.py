from django.urls import path
from WebsiteSystem import views
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('sponsors/all/', views.SponsorGetView.as_view()),
    path('sponsors/', views.SponsorPostView.as_view()),
    path('sponsors/<int:pk>/', views.SponsorDelView.as_view()),
    path('teams/',views.TeamView.as_view()),
    path('teams/<int:pk>/',views.TeamEditView.as_view()),
    path('news-feed/<int:page_number>/',views.NewsFeedView.as_view()),
    path('edit-news-feed/<int:id>/',views.EditNewsFeedView.as_view()),
    path('news-feed/',views.PostNewsFeedView.as_view()),
    path('faq/<int:id>/',views.DeleteFaqView.as_view()),
    path('faq/',views.FAQView.as_view()),
    path('highlights/all/',views.AllHighlights.as_view()),
    path('highlights/<int:id>/',views.Highlights.as_view()),
    path('highlights/active/',views.ActiveHighlights.as_view()),
    path('highlights/',views.PostHighlight.as_view()),
    path('events/<int:id>/', views.Events.as_view()),
    path('events/all/', views.AllEvents.as_view()),
    path('events/active/', views.ActiveEvents.as_view()),
    path('events/', views.PostEvent.as_view()),
    path('users/all/', views.AllUsers.as_view()),
    path('user/<int:id>/',views.UserView.as_view()),
    path('groups/all/',views.GroupsView.as_view()),
    path('remove-from/<int:type>/<int:first_id>/<int:second_id>/',views.RemoveFromView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)