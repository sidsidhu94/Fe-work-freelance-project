from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.tokens import AccessToken
from account.models import ChatMessage
import json
from channels.db import database_sync_to_async
from django.utils import timezone
# from django.contrib.auth import get_user_model
from account.models import UserAccount

# User = get_user_model()

class ChatRoomConsumer(AsyncWebsocketConsumer):
    

    async def connect(self):
        
        await self.accept()
        print(self.scope)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_name = f"user_{self.scope['user'].id}"
        print(self.room_name,"room name")

        self.room_group_name = f"chat_{self.room_name}"

        print("here.........",self.room_group_name)
        
       

        
        

        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # await self.accept()

    async def disconnect(self,close_code):
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        
    @database_sync_to_async
    def get_user(self, user_id):
        return UserAccount.objects.get(pk=user_id)
    
    @database_sync_to_async
    def save_message(self, message_content, sender, receiver):
        message = ChatMessage.objects.create(sender=sender, receiver=receiver, content=message_content, timestamp=timezone.now())
        message.save()

    async def receive(self, text_data = None):
        print(text_data,'jhwgfwejfbwekhfgwejfbweh')
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]
        sender_id = text_data_json["sender"]
        receiver_id = text_data_json["recipient"]
        
        
        
        sender = await self.get_user(sender_id)
        receiver = await self.get_user(receiver_id)
        print(message_content,sender,receiver,"hereeeeee")

        # sender = get_user_model().objects.get(id = sender_id)
        # receiver = User.objects.get(id = receiver_id)
        # sender = UserAccount.objects.get(pk=sender_id)
        # receiver = UserAccount.objects.get(pk=receiver_id)
    

        # Save the message to the database

        # await self.save_message(message_content , sender , receiver) 
        await self.save_message(message_content, sender, receiver)
        await self.channel_layer.group_send(
        self.room_group_name, {"type": "chat.message", "message": message_content, "sender": sender, "receiver": receiver}
    )
        
        # message = ChatMessage.objects.create(sender=sender, receiver=receiver, content=message_content,timestamp=timezone.now())

        # message.save()

        # Send message to user's personal chat group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message_content, "sender": sender,"receiver ":receiver}
        )


    
    # async def save_message(self, message_content, sender, receiver):
    
    #     message = ChatMessage.objects.create(sender=sender, receiver=receiver, content=message_content, timestamp=timezone.now())
    #     message.save()


    async def chat_message(self, event):
        message_content = event["message"]
        sender = event["sender"]
        # receiver = event["receiver"]

        sender_data = {'id': sender.id, 'email': sender.email} 
        # receiver_data = {'id': receiver.id, 'email': receiver.email} 
        # print(receiver_data)
        
        await self.send(text_data=json.dumps({"type": "message", "message": message_content, "sender": sender_data}))


        # Send message to WebSocket
        # await self.send(text_data=json.dumps({"type":"message","message": message_content, "sender": sender,"receiver":receiver}))

        

    