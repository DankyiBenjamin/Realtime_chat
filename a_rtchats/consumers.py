from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
# from .models import *
import json
from django.db import transaction


class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        from .models import ChatGroup
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(
            ChatGroup, group_name=self.chatroom_name)

        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )
        # add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()
        self.accept()

    def disconnect(self, close_code):
        from .models import ChatGroup

        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )
        # remove user from online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    def receive(self, text_data):
        from .models import GroupMessages
        text_data_json = json.loads(text_data)

        body = text_data_json['body']

        message = GroupMessages.objects.create(
            body=body,
            author=self.user,
            group=self.chatroom
        )

        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def message_handler(self, event):
        from .models import GroupMessages

        message_id = event['message_id']
        message = GroupMessages.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user,
        }

        html = render_to_string(
            "a_rtchats/partials/chat_message_p.html", context=context)
        self.send(text_data=html)
    @transaction.atomic
    def update_online_count(self):
        # get the online users count and subtract the current user
        online_count = self.chatroom.users_online.count() - 1
        event = {
            'type': 'online_count_handler',
            'online_count': online_count,
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def online_count_handler(self, event):
        online_count = event['online_count']
        context = {
            'online_count': online_count,
        }

        html = render_to_string(
            "a_rtchats/partials/online_count_p.html", context=context)
        self.send(text_data=html)
