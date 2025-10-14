# matching/urls.py

from django.urls import path
from .views import MatchUserView, SwipeActionView, MatchListView

urlpatterns = [

    path('match/', MatchUserView.as_view(), name='match_user'),
    path('swiped/', SwipeActionView.as_view(), name='swipe_action'),
    path('matches/', MatchListView.as_view(), name='match_list'),
]