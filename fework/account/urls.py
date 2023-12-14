from django.urls import path
from .views import RegisterView,LoginUser,LoginAdmin,VerifyOtpView,UserLogoutView,UserView,RemoveUser,EditUser,AddUser,LogoutView,ProfileView
from .views import UserProfileView,UserWorkView,UserWorksView,MyInbox,GetMessages,SendMessage,AdminWorksView,VerifyWorkView,RejectWorkView,UserprofileListView,AllWorksPostedView
from .views import WorksComments,WorkCommentsView,AppreciateWorkView,PremiumMembershipView,AllPremiumMembershipsView,TransactionAPIView,create_razorpay_order,FollowUserView,Get_User,FollowWorksPostedView

urlpatterns = [
    path('register/',RegisterView.as_view()),
    path('login/',LoginUser.as_view()),
    path('admin_login/',LoginAdmin.as_view()),
    path('verify_otp/',VerifyOtpView.as_view()),
   
    
    path('userlogout/',UserLogoutView.as_view()),


    path('dashboard/',UserView.as_view()),
    path('remove/<int:pk>',RemoveUser.as_view()),
    path('edit/<int:pk>',EditUser.as_view()),
    path('adduser/',AddUser.as_view()),
    path('logout/',LogoutView.as_view()),


    path('user_profile/',ProfileView.as_view()),
    path('profile/update/', ProfileView.as_view(), name='profile-update'),
    # path('follow/<int:user_id>/', FollowAPIView.as_view(), name='follow'),


    path('user_profile_display/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('user_work_post/',UserWorkView.as_view()),

    path('user-work/<int:user_id>/', UserWorksView.as_view()),
    path('verify-admin/', AdminWorksView.as_view()),
    path('verify-work/<int:work_id>/', VerifyWorkView.as_view(), name='verify_work'),
    path('reject-work/<int:work_id>/', RejectWorkView.as_view(), name='reject_work'),

     
    path("my-messages/<user_id>/",MyInbox.as_view()),
    path("get-messages/<int:sender_id>/<int:receiver_id>/",GetMessages.as_view()),
    path("send-message/",SendMessage.as_view()),
    
    path('userprofiles/', UserprofileListView.as_view(), name='userprofile-list'),

    path('all_works/', AllWorksPostedView.as_view(), name='all_works'),
    path('follow_works/<int:user_id>/', FollowWorksPostedView.as_view(), name='all_work'),

    # path('add-follower/', AddFollower.as_view(), name='add-follower'),

  

    # path('toggle-follow/', ToggleFollowView.as_view(), name='toggle-follow'),

    # ///////////comments///////////
    path('workcomment/', WorksComments.as_view(), name='work_comment'),
    path('work-comment/<int:work_id>/',WorkCommentsView.as_view(),name='work_comments_view'),

    path('appreciate/<int:work_id>/', AppreciateWorkView.as_view(), name='appreciate_work'),
    path('add-premium/', PremiumMembershipView.as_view()),
    path('all-premium/', AllPremiumMembershipsView.as_view(), name='all_premium'),
    path('verifygateway',TransactionAPIView.as_view()),
    path('paymentgateway',create_razorpay_order),

    # path('user_connection/<int:user_account_id>/follow', UserConnectionView.as_view(), name='user-connection-detail'),
    path('follow_user/<int:user_account_id>/', FollowUserView.as_view(), name='follow-user'),
    path('follow_status/<int:user_id>', FollowUserView.as_view(), name='follow_status'),

    path('user-messages/<int:user_account_id>/', Get_User.as_view(), name='user-messages'),

    



   
]





 # path('user_login/',LoginUser.as_view()),
#  path('user_logout/',UserLogoutView.as_view()),