from django.urls import path
import chat.routing


websocket_urlpatterns = chat.routing.websocket_urlpatterns
