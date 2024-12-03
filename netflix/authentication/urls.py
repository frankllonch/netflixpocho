from django.urls import path
from .views import signup, UserProfileView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', signup, name='signup'),  # Add the signup route
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]