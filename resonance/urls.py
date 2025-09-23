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
# spotapp/urls.py
from django.urls import path
from users import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('profile/<str:spotify_id>/', views.profile_detail, name='profile_detail'),
    path('profile/<str:spotify_id>/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.spotify_logout, name='spotify_logout'),
]

