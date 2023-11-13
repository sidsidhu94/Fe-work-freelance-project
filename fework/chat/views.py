from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from account.models import ChatMessage
from .serializer import ChatMessageSerializer

from account.models import UserAccount
# Create your views here.



# class ChatRoomAPIView(APIView):
#     def post(self, request, room_name):
#         # Get the channel_name from the request data
#         channel_name = request.data.get('channel_name')

#         if not channel_name:
#             return Response({'error': 'channel_name is required'}, status=status.HTTP_400_BAD_REQUEST)

#         # Execute the logic from ChatRoomConsumer
#         room_group_name = f"chat_{room_name}"

#         # Join room group
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_add)(room_group_name, channel_name)

#         # Send a message to the room group
#         async_to_sync(channel_layer.group_send)(
#             room_group_name, {"type": "chat.message", "message": "Hello, everyone!"}
#         )

#         return Response({"status": "Room connected and message sent."}, status=status.HTTP_200_OK)
    

class ChatRoomAPIView(APIView):
    def post(self, request, room_name, sender_id, receiver_id):
        
        channel_name = request.data.get('channel_name')
        print(request.headers,"...............................here")

       
        
        
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
        if not channel_name:
            return Response({'error': 'channel_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            sender = UserAccount.objects.get(pk=sender_id)
            receiver = UserAccount.objects.get(pk=receiver_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        
        room_group_name = f"chat_{room_name}"

       
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_add)(room_group_name, channel_name)

        
        message_content = "Hello, everyone!"
        chat_message = ChatMessage.objects.create(
            user=request.user,
            sender=sender,
            receiver=receiver,
            message=message_content,
        )

        
        serializer = ChatMessageSerializer(chat_message)
        serialized_data = serializer.data

        
        async_to_sync(channel_layer.group_send)(
            room_group_name, {"type": "chat.message", "message": serialized_data}
        )

        return Response({"status": "Room connected and message sent."}, status=status.HTTP_200_OK)




# class ChatRoomAPIView(APIView):
#     def post(self, request, room_name,sender_id, receiver_id):
        
#         channel_name = request.data.get('channel_name')


#         if not request.user.is_authenticated:
#             return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

#         if not channel_name:
#             return Response({'error': 'channel_name is required'}, status=status.HTTP_400_BAD_REQUEST)

#         user = request.user

        
#         room_group_name = f"chat_{room_name}"

        
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_add)(room_group_name, channel_name)

        
#         message_content = "Hello, everyone!"

        
#         chat_message = ChatMessage.objects.create(
#             user=user,
#             sender=user,
#             receiver=None,  
#             message=message_content,
#         )

        
#         serializer = ChatMessageSerializer(chat_message)
#         serialized_data = serializer.data

#         async_to_sync(channel_layer.group_send)(
#             room_group_name, {"type": "chat.message", "message": serialized_data}
#         )

#         return Response({"status": "Room connected and message sent."}, status=status.HTTP_200_OK)














# class RoomAPIView(APIView):
#     def get(self, request, room_name):
#         # Your logic for handling GET requests goes here
#         return Response({"room_name": room_name})

#     def post(self, request, room_name):
#         # Your logic for handling POST requests goes here
#         return Response({"room_name": room_name}, status=status.HTTP_201_CREATED)

#     def put(self, request, room_name):
#         # Your logic for handling PUT requests goes here
#         return Response({"room_name": room_name})

#     def delete(self, request, room_name):
#         # Your logic for handling DELETE requests goes here
#         return Response(status=status.HTTP_204_NO_CONTENT)