import json

from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin, action

from users.serializers import UserSerializer
from .models import Message, Room
from .serializers import MessageSerializer, RoomSerializer


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"

    @action()
    async def join_room(self, pk, **kwargs):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.send_json({
                "error": "Authentication required to join rooms.",
                "action": "join_room",
                "request_id": kwargs.get("request_id")
            })
            return

        self.room_subscribe = pk
        await self.message_activity.subscribe(room=pk)
        await self.add_user_to_room(pk)
        
        # Send confirmation to the client
        await self.send_json({
            "message": f"Successfully joined room {pk}",
            "action": "join_room",
            "request_id": kwargs.get("request_id")
        })

    @action()
    async def leave_room(self, pk, **kwargs):
        await self.message_activity.unsubscribe(room=pk)
        
        # Remove user from room's current_users ManyToMany field
        await self.remove_user_from_room(pk)

    @action()
    async def create_message(self, text, **kwargs):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.send_json({
                "error": "Authentication required to send messages.",
                "action": "create_message",
                "request_id": kwargs.get("request_id")
            })
            return

        room_id = getattr(self, "room_subscribe", None)
        if not room_id:
            await self.send_json({
                "error": "You must join a room before sending messages.",
                "action": "create_message",
                "request_id": kwargs.get("request_id")
            })
            return

        try:
            room = await self.get_room(pk=room_id)
        except Room.DoesNotExist:
            await self.send_json({
                "error": "Room does not exist.",
                "action": "create_message",
                "request_id": kwargs.get("request_id")
            })
            return

        await database_sync_to_async(Message.objects.create)(
            room=room,
            user=user,
            text=text                 
        )

    @model_observer(Message)
    async def message_activity(self, message, observer=None, **kwargs):
        # Sends the message down the WebSocket to the client
        await self.send_json(message)

    @message_activity.serializer
    def message_activity(self, instance: Message, action, **kwargs):
        return MessageSerializer(instance).data

    @message_activity.groups_for_signal
    def message_activity(self, instance: Message, **kwargs):
        yield f'room__{instance.room_id}'

    @message_activity.groups_for_consumer
    def message_activity(self, room=None, **kwargs):
        if room is not None:
            yield f'room__{room}'

    # --- Helper methods to interact with the database safely (sync to async) ---

    @database_sync_to_async
    def get_room(self, pk: int) -> Room:
        return Room.objects.get(pk=pk)

    @database_sync_to_async
    def add_user_to_room(self, pk: int):
        try:
            room = Room.objects.get(pk=pk)
            if self.scope["user"].is_authenticated:
                room.current_users.add(self.scope["user"])
        except Room.DoesNotExist:
            pass

    @database_sync_to_async
    def remove_user_from_room(self, pk: int):
        try:
            room = Room.objects.get(pk=pk)
            if self.scope["user"].is_authenticated:
                room.current_users.remove(self.scope["user"])
        except Room.DoesNotExist:
            pass