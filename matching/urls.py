from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    # main page that shows the swipe interface
    path('discover/', views.DiscoverPageView.as_view(), name='discover_page'),
    
    # API Endpoints 
    # handles the swipe action
    path('api/swipe/', views.SwipeActionAPI.as_view(), name='api_swipe_action'),
]