from django.urls import path
from . import views

app_name = 'messenger'

urlpatterns = [
   path('messenger', views.messenger, name='messenger'),
   path("<int:user_id>/", views.messages_from_conversations, name="messages_from_conversations"),
   path('send_message/<int:user_id>/', views.send_message_from_profile, name='send_message_from_profile'),
]