from django.contrib import admin
from .models import Room, Message

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'created_at')
