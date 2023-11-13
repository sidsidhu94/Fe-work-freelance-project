from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.tokens import AccessToken

import json


class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Authenticate the user using the provided token in the query parameters
        token = self.scope.get("query_string").decode("utf-8").split("token=")[1]
        try:
            access_token = AccessToken(token)
            self.scope["user"] = access_token.user
        except Exception as e:
           
            print(f"Authentication error: {e}")
            await self.close()
            return 

    # async def connect(self):
    #     self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
    #     self.room_group_name = f"chat_{self.room_name}"

       
    #     await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    #     await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))




# # class ChatRoomConsumer(WebsocketConsumer):
#     # async def connect(self):
#     #     self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#     #     self.room_group_name = f"chat_{self.room_name}"
        
#     #     async_to_sync(self.channel_layer.group_add)(
#     #         self.room_group_name, self.channel_name
#     #     )

# class ChatRoomConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#         # Receive message from WebSocket
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )

#     # Receive message from room group
#     def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))