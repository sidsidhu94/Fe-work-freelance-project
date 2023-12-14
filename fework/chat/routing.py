from django.urls import re_path,path
from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$',consumers.ChatRoomConsumer)
    path('ws/chat/<str:room_name>/', consumers.ChatRoomConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<sender_id>\w+)/(?P<receiver_id>\w+)/$', consumers.ChatRoomConsumer)



]