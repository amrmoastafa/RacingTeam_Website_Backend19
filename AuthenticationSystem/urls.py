from django.urls import path
from AuthenticationSystem import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as rest_views
from rest_framework_jwt.views import verify_jwt_token

# from .views import views


urlpatterns = [
    path('register/', views.SignUpView.as_view()),
    path('login/',views.SignInView.as_view()),
    path('social/',views.SocialAuthView.as_view()),
    path('api-token-auth/', rest_views.obtain_auth_token),
    path('token-verify/',verify_jwt_token),
    path('forget-password/',views.ForgetPasswordView.as_view()),
    path('login/',views.SignInView.as_view()),
    path('change-password/',views.ChangePasswordView.as_view())
]


urlpatterns = format_suffix_patterns(urlpatterns)
