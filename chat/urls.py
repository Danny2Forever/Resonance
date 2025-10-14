from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_list_view, name="chat_page"),
    path("api/<int:chat_id>/", views.chat_detail, name="chat_detail_api"),
    path("api/<int:chat_id>/send/", views.send_message, name="send_message_api"),
]