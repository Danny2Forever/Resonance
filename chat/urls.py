from django.urls import path
from . import views

urlpatterns = [
    path("<int:chat_id>/", views.chat_detail, name="chat_detail"),
    path("<int:chat_id>/send/", views.send_message, name="send_message"),
]