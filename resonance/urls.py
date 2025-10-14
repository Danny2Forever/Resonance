"""
URL configuration for resonance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.contrib import admin
from users import views
from django.conf.urls.static import static
from django.conf import settings
from users.views import *
from matching.views import *
from admin_dashboard.views import AdminDashboardView
from django.shortcuts import render

def landing_page(request):
    return render(request, "landing.html")

def test_chat_view(request):
    return render(request, 'chat/chat.html')

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('login/', SpotifyLoginView.as_view(), name='spotify_login'),
    path('callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('profile/<str:spotify_id>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/<str:spotify_id>/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('logout/', SpotifyLogoutView.as_view(), name='spotify_logout'),
    path('match/', MatchUserView.as_view(), name='match_user'),
    path('swiped/', SwipeActionView.as_view(), name='swipe_action'),
    path('chat/', include('chat.urls')),
    path("dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path('', include('matching.urls')),
]
