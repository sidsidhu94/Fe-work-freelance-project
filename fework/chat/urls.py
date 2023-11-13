from django.urls import path

from .views import ChatRoomAPIView



urlpatterns = [
    # path("", views.index, name="index"),
    # path("<str:room_name>/", ChatRoomAPIView.as_view(), name='room'),######first url
    # path("<str:room_name>/<str:user_id>/", ChatRoomAPIView.as_view(), name='room'),
    path("<str:room_name>/<sender_id>/<receiver_id>", ChatRoomAPIView.as_view(), name='room'),
    

    

]