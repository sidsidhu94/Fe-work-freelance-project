from django.http import Http404
from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login,logout
from rest_framework.response import Response
from datetime import timedelta
import jwt,datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.conf import settings 
from django.core.mail import send_mail
import random
import string
from django.core.mail import  BadHeaderError
from django.conf import settings
from smtplib import SMTPException
from django.db.models import Q,Subquery,OuterRef,Count
import cloudinary
import cloudinary.uploader

from rest_framework import generics
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

import razorpay
from .main import RazorpayClient
rz_client = RazorpayClient()

import smtplib
from email.message import EmailMessage

from .models import UserAccount,Userprofile,Userwork,ChatMessage,UserConnection,WorkAppreciation,Jobs,Payment
from .models import PremiumMembership as PremiumMembershipModel

User = UserAccount

from .serializer import  UserCreateSerializer, UserSerializer,OTPVerificationSerializer,ImageSerializer,UserprofileSerializer,ChatMessageSerializer,WorkAppreciationSerializer,TransactionSerializer,UserJobSerializer

from .serializer import UserWorkSerializer,WorkImageSerializer,UserWorksSerializer,MessageSerializer,UserConnectionSerializer,UserprofilesSerializer,WorkscommentsSerializer,PremiumMembership,UserMessageprofileSerializer
# from .serializer import ,UserAccountSerializer
# from .emails import sent_otp_via_email
# Create your views here.

from rest_framework.permissions import BasePermission


# ///////////////////////permission class////////////////////
# ///////////////////////permission class////////////////////
# ///////////////////////permission class////////////////////
class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow anyone to view the endpoint
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Only allow authenticated users to modify their own data
        return obj.user == request.user
# ///////////////////////permission class////////////////////
# ///////////////////////permission class////////////////////
# ///////////////////////permission class////////////////////    
    
class RegisterView(APIView):
    def post(self,request):
        data = request.data

        print("aghcdsjhcdckl")

        
        data['otp'] = self.generate_otp()
        
        serializer = UserCreateSerializer(data= data)
  
        if serializer.is_valid():
            
            serializer.save()
            self.sent_otp_via_email(serializer.data['otp'],serializer.data['email'])


            print(serializer.data)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
            
            # # email = user.email
            # # print(email,"+++++++++++++++++++++")
            # print(otp,"+++++++++++++++++++++")

        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
            
        
           

        
    
    def generate_otp(self):
         otp = random.randint(100000, 999999)
         return otp
    
    def sent_otp_via_email(self, otp,email):
        print(email,"++++++++++")
        print(otp,"++++++++++++")
        subject = "Your account verification email"
        message = f'Your OTP is: {otp}'
        email_from = 'electronshop409@gmail.com'
        to_email=email
        print(to_email)
        print(email_from)
        

        

        try:
            print(email_from)
            print(to_email)
            print(message)
            send_mail(subject, message, email_from, [to_email],fail_silently=False)
        except BadHeaderError as e:
           
            print("BadHeaderError:", e)
        except SMTPException as e:
            
            print("SMTPException:", e)
        except Exception as e:
            
            print("Other Exception:", e)


class VerifyOtpView(APIView):
    def post(self,request):
        data = request.data

        print(data)
        serializer = OTPVerificationSerializer(data = data)
        print(serializer)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['verifyotp']

            user = UserAccount.objects.get(email = email)

            if user.otp == otp :
                user.is_active = True
                user.save()
                return Response({'message': 'OTP verified and is_verified set to True'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




 
    


class LoginUser(APIView):
    

    def post(self,request):
        
        print("rferhfbejrhkfberhj")
        if request.method =="POST":
            email =request.data['email']
            
            password = request.data['password']

            print(email,password)

            user = UserAccount.objects.filter(email = email).first()
            print(user)

            if user is None or user.delete == True or user.is_active == False:
                return Response({"message":"Not a registered user"})
            
            if not user.check_password(password):
                return Response({"message":"Incorrect Password"})
            
            payload = {
                'id': user.id,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 60),
                'iat' : datetime.datetime.utcnow()
            }

        secret_key = settings.SECRET_KEY
        algorithm = 'HS256'

        token = jwt.encode(payload, secret_key,algorithm=algorithm)

        response  = Response()

        response.data ={
            'token' : token,
            'message' : "userlogin",
            "username" : user.firstname +" " + user.lastname,
            "user_id" : user.id
            
            
        }

        return response
    

class UserLogoutView(APIView):
    

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class LoginAdmin(APIView):
    def post(self,request):
        if request.method =="POST":
            email =request.data['email']
            password = request.data['password']

            User = get_user_model()

            user = User.objects.filter(email = email,is_superuser = True).first()

            if user is None:
                return Response({"message":"not Authorized"})
            
            if not user.check_password(password):
                return Response({"message":"Incorrect Password"})
            
            
            payload = {
                'id': user.id,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 60),
                'iat' : datetime.datetime.utcnow()
            }

        secret_key = 'secret'
        algorithm = 'HS256'

        token = jwt.encode(payload, secret_key,algorithm=algorithm)

        response  = Response()

        response.data ={
            'token' : token,
            'message' : "adminlogin",
            
        }
        

        return response

class UserView(APIView):
   
    
    def get(self,request):
       
        users = User.objects.filter(is_admin = False,delete = False)
        serialized_users = [{'id' : user.id , 'username': user.firstname, 'email': user.email, 'phonenumber' : user.phonenumber} for user in users]
        
        return Response(serialized_users)
    
# class UserProfileView(APIView):
#     def get(self,request):
#         user = User.objects.get(user = request.data)


#         serializer = ProfileSerializer(user,data = request.data)
        



class EditUser(APIView):
    def put(self,request,pk):
        user = User.objects.get(pk = pk)
        serializer = UserSerializer(user, data= request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveUser(APIView):


    def delete(self,request, pk):
        
        user = User.objects.get(pk=pk)
        serializer =UserSerializer(user)
        print(serializer.data)

        user.delete = True
        user.save()
        
        return Response({'message': 'User blocked successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class AddUser(APIView):

    def post(self,request):
        data = request.data
        

        serializer = UserCreateSerializer(data = data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        user = serializer.create(serializer.validated_data)
        user = UserSerializer(user)
        
        
    
        return Response(user.data,status=status.HTTP_201_CREATED)
    
class LogoutView(APIView):
    

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
    


# class ProfileView(APIView):
#     def post(self, request):
#         user_id = request.data.get('user')




class ProfileView(APIView):
   
    def post(self, request):
        
        user_id = request.data.get('userId')
        profile_pic = request.data.get('profile_image')
        username = request.data.get('username')
        country = request.data.get('country')
        description = request.data.get('description')
        skills  = request.data.get('skills')

        
        
        if not profile_pic :
            return Response({'error': 'image are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not username :
            return Response({'error': 'username required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not country :
            return Response({'error': 'enter your country  '}, status=status.HTTP_400_BAD_REQUEST)
        
        if not description :
            return Response({'error': 'description required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not skills :
            return Response({'error': 'enter your skills'}, status=status.HTTP_400_BAD_REQUEST)


        # user = UserAccount.objects.get(email = user_id)
        # user = UserAccount.objects.filter(Q(email__iexact=user_id)).first()
        try:
            user = UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

       

        # print(user,'.........................here')

        result = cloudinary.uploader.upload(profile_pic) 
        urls = result.pop('url')
        # print(result.pop('url'),"...............here")

        print(urls,"...............here")

       

        
     

        user_profile = {
            
            'user_id':user.id,
            'profile_pic':urls,  
            'username':username,
            'country':country,
            'description':description,
            'skills':skills

        }

   
        print(user_profile,"shkwghudhkjwbhjfhwfkhwerfurhgfuyergfuyerbfherjkfgherfherjfnejlgehr")

        serializer = ImageSerializer(data=user_profile)

        print(serializer)
        
        
        if serializer.is_valid():
            

            serializer.save()
            print(serializer.data,"..........................")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        return self.update_profile(request)

    # def patch(self, request):
    #     return self.update_profile(request)

    def patch(self, request):
        user_id = request.data.get('userId')

        try:
            user = UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Extract updated data from the request
        profile_pic = request.data.get('profile_image')
        username = request.data.get('username')
        country = request.data.get('country')
        description = request.data.get('description')
        skills = request.data.get('skills')

        # Update fields if they are provided
        if profile_pic:
            result = cloudinary.uploader.upload(profile_pic)
            urls = result.pop('url')
            user.profile_pic = urls

        if username:
            user.username = username

        if country:
            user.country = country

        if description:
            user.description = description

        if skills:
            user.skills = skills

        # Save the updated user instance
        user.save()

        # Serialize the updated data and return the response
        serializer = ImageSerializer(user,)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserProfileView(APIView):
    
    def get(self, request, user_id):
        print(request.headers,",.......,,,,,,,,,,>>>>>>>>>>>>>>>>>>>>>>>..")
        
        try:
            user_profile = Userprofile.objects.get(user_id=user_id)
            serializer = UserprofileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Userprofile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)



# class UserWork(APIView):
#     def post(self, request):
#         user_id = request.data.get('userId')
#         work_images = request.data.get('')
#         work_description = request.data.get('')
#         work_caption = request.data.get('')
        


#         try:
#             user = UserAccount.objects.get(pk=user_id)
#         except UserAccount.DoesNotExist:
#             return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)



class UserWorkView(APIView):
    def post(self, request):
        user_id = request.data.get('userId')
        work_description = request.data.get('textWritten')
        work_caption = request.data.get('captionEntered')

        try:
            user = UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        print(user, "hello hereeeeeee don't worry")

        user_work_serializer = UserWorkSerializer(data={
            'user': user.id,
            'work_description': work_description,
            'work_caption': work_caption
        })

        if user_work_serializer.is_valid():
            user_work_serializer.save()

            images = request.data.get('selectedimages')
            print(images, ".............................here")

            for image in images:
                result = cloudinary.uploader.upload(image)
                work_image = result.pop('url')
                print(work_image, ".............................here")

                print(user_work_serializer.data, "dataaaaaaaaaaaa,jdfjhbh")

                work_image_serializer = WorkImageSerializer(
                    data={'user_work': user_work_serializer.instance.id, 'image': work_image}
                )
                if work_image_serializer.is_valid():
                    work_image_serializer.save()
                else:
                    print(work_image_serializer.errors)
                    return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'User work and images uploaded successfully'}, status=status.HTTP_201_CREATED)
        else:
            print(user_work_serializer.errors)
            return Response({'error': 'User work creation failed'}, status=status.HTTP_400_BAD_REQUEST)


    # def post(self, request):
    #     user_id = request.data.get('userId')
    #     work_description = request.data.get('textWritten')
    #     work_caption = request.data.get('captionEntered')


    #     # print(request.data)
        

    #     try:
    #         user = UserAccount.objects.get(pk=user_id)
    #     except UserAccount.DoesNotExist:
    #         return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    #     print(user,"hello hereeeeeee dont worry")
        
    


        
    #     user_work_serializer = UserWorkSerializer(data={
    #         'user': user.id,
    #         'work_description': work_description,
    #         'work_caption': work_caption
    #     })
        

    #     if user_work_serializer.is_valid():
    #         print(user_work_serializer,"just testing the error ")
            
    #         user_work_serializer.save()  

            
 
            
            
    #         images = request.data.get('selectedimages')
    #         print(images,".............................here")
            
    #         for image in images:
                

    #             result = cloudinary.uploader.upload(image)
                
                
    #             work_image = result.pop('url')
    #             print(work_image,".............................here")

    #             print(user_work_serializer.data,"dataaaaaaaaaaaa,jdfjhbh")
                
    #             work_image_serializer = WorkImageSerializer(data={'user_work': user_work_serializer.instance.id, 'image': work_image})
    #             if work_image_serializer.is_valid():

    #                 work_image_serializer.save() 
    #             else:
                    
    #                 return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

    #         return Response({'message': 'User work and images uploaded successfully'}, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response({'error': 'User work creation failed'}, status=status.HTTP_400_BAD_REQUEST)







# class UserWorkview(APIView):
#     def get(self,request,user_id):
#         try:
#             user =  Userprofile.objects.get(user_id=user_id)
#             serializer = UserprofileSerializer(user)
            
            
#             user_works = Userwork.objects.filter(user=user)
#             user_work_serializer = UserWorkSerializer(user_works, many=True)

#             response_data = {
#                 'user_profile': serializer.data,
#                 'user_works': user_work_serializer.data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)
#         except Userprofile.DoesNotExist:
#             return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

class UserWorksView(APIView):
    def get(self, request, user_id):
        
        try:
            
            user_works = Userwork.objects.filter(user_id=user_id, is_verified=True)
            
            
            if not user_works.exists():
                raise Http404('No verified user works found')

            user_work_serializer = UserWorksSerializer(user_works, many=True)
            print(user_work_serializer,"this is testing kfnw,fwefkkjwefnkewwefkjnwefewfkjf")
            return Response(user_work_serializer.data, status=status.HTTP_200_OK)
        except Userwork.DoesNotExist:
            return Response({'error': 'User work not found'}, status=status.HTTP_404_NOT_FOUND)
        

class AdminWorksView(APIView):
    def get(self, request):
        try:

            # user_works = Userwork.objects.all()  
            user_works = Userwork.objects.filter(is_verified=False)
            
            if not user_works.exists():
                raise Http404('No user works found')

            user_work_serializer = UserWorksSerializer(user_works, many=True)
            return Response(user_work_serializer.data, status=status.HTTP_200_OK)
        except Userwork.DoesNotExist:
            return Response({'error': 'User work not found'}, status=status.HTTP_404_NOT_FOUND)
        


class VerifyWorkView(APIView):
    def post(self, request, work_id):
        try:
            user_work = Userwork.objects.get(pk=work_id)
        except Userwork.DoesNotExist:
            return Response({'error': 'Work not found'}, status=status.HTTP_404_NOT_FOUND)

        
        # if not request.user.is_superuser:
        #     return Response({'error': 'Unauthorized to verify work'}, status=status.HTTP_403_FORBIDDEN)

        
        user_work.is_verified = True
        user_work.save()

        
        return Response({'message': 'Work verified successfully'}, status=status.HTTP_200_OK)
    
class AllWorksPostedView(APIView):
    def get(self,request):
        
        # user_works = Userwork.objects.filter(is_verified=True)
        user_works = Userwork.objects.filter(is_verified=True)
        print(user_works,'efcewvhergvbkwjehrvberwgvhjer')

        print(user_works)
        serializer = UserWorksSerializer(user_works,many= True)

        
        return Response(serializer.data)

class RejectWorkView(APIView):
    def post(self, request, work_id):
        try:
            user_work = Userwork.objects.get(pk=work_id)
        except Userwork.DoesNotExist:
            return Response({'error': 'Work not found'}, status=status.HTTP_404_NOT_FOUND)

        
        # if not request.user.is_superuser:
        #     return Response({'error': 'Unauthorized to reject work'}, status=status.HTTP_403_FORBIDDEN)

        
        user_work.is_verified = False
        user_work.save()

        
        return Response({'message': 'Work rejected successfully'}, status=status.HTTP_200_OK)






class MyInbox(generics.ListAPIView):
      
      serializer_class = ChatMessageSerializer

      def get_queryset(self):
          user_id = self.kwargs['user_id']
          

          
          messages = ChatMessage.objects.filter(
              id__in = Subquery(
                  UserAccount.objects.filter(
                      Q(sender__receiver = user_id)|
                      Q(receiver__sender = user_id)
                  ).distinct().annotate(
                      last_msg = Subquery(
                          ChatMessage.objects.filter(
                              Q(sender = OuterRef('id'),receiver = user_id)|
                              Q(receiver = OuterRef('id'),sender = user_id)
                          ).order_by("-id")[:1].values_list("id",flat=True)
                      )
                  ).values_list("last_msg",flat=True).order_by("-id")
              )
          ).order_by("-id")
          print(messages,"..w.wed.wedwedwed.wedwed.we")
          
          return messages
      
class GetMessages(generics.ListAPIView):
    # serializer_class = ChatMessage
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        sender_id = self.kwargs['sender_id']
        receiver_id = self.kwargs['receiver_id']


        messages = ChatMessage.objects.filter(
            sender__in = [sender_id, receiver_id],
            receiver__in = [sender_id, receiver_id]

            )
        return messages

class SendMessage(generics.CreateAPIView):
    serializer_class = MessageSerializer




# @method_decorator(login_required, name='dispatch')
# class FollowAPIView(APIView):
#     def get_object(self, user_id):
#         return get_object_or_404(UserConnection, id=user_id)

#     def get(self, request, user_id, *args, **kwargs):
#         user_to_toggle = self.get_object(user_id)
#         user, is_following = request.user.user_connections.get_or_create_follow(user_to_toggle)
#         serializer = UserConnectionSerializer(user_to_toggle)
#         return Response({'is_following': is_following, 'user_data': serializer.data})

#     def post(self, request, user_id, *args, **kwargs):
#         user_to_toggle = self.get_object(user_id)
#         user, is_following = request.user.user_connections.get_or_create_follow(user_to_toggle)
        
#         if is_following:
#             user.follows.remove(user_to_toggle)
#         else:
#             user.follows.add(user_to_toggle)

#         serializer = UserConnectionSerializer(user_to_toggle)
#         return Response({'is_following': not is_following, 'user_data': serializer.data})







class UserprofileListView(generics.ListAPIView):
    queryset = Userprofile.objects.all()
    serializer_class = UserprofilesSerializer





# user follow function /////////////////////////////////



# class UserConnectionListCreateView(generics.ListCreateAPIView):
#     serializer_class = UserConnectionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return UserConnection.objects.filter(user_account=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user_account=self.request.user)

# class UserConnectionDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = UserConnectionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return UserConnection.objects.filter(user_account=self.request.user)




# class ToggleFollowView(APIView):
#     def post(self, request, pk, format=None):
        
#         other_user = get_object_or_404(User, pk=pk)
#         print(other_user ,"ewhgewrfvgherfvberwjfbhwerfwqfjwqhfjwfwqjfbwqejfgvweqghfw")

#         if request.user == other_user:
#             return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

#         user_connection, created = UserConnection.objects.get_or_create(user_account=request.user)
        
#         if other_user in user_connection.follows.all():
#             user_connection.follows.remove(other_user)
#             followed = False
#         else:
#             user_connection.follows.add(other_user)
#             followed = True

#         return Response({"followed": followed}, status=status.HTTP_200_OK)

        


# class AddFollower(APIView):
    # permission_classes = [IsAuthenticated ]

    def post(self, request, format=None):
    
        
        user_id = request.data['user_id']
        follow_id = request.data['follow_id']
        
        user_connection = UserConnection.objects.get(pk=user_id)
       
        # user_connection = UserConnection.objects.get(user_id=user_id)
        # user_connection = UserConnection.objects.get(user_account__user_id=user_id)
        
        # user_connection = UserConnection.objects.get(user_account__user_id=user_id)



        print(user_connection,'just testing user')
        # user_to_follow = UserConnection.objects.get(user_account_id=follow_id)
        user_to_follow = UserConnection.objects.filter(pk=follow_id)
        print(user_to_follow,"sdkchsdcjhsdgchjsdcgsducsdjchsdgcys")
                                                    
        user_connection.follow_user(user_to_follow)
        user_connection_serializer = UserConnectionSerializer(user_connection)

        return Response({
            'status': status.HTTP_200_OK,
            'data': user_connection_serializer.data,
            'message': f'User {user_id} is now following {follow_id}'
        })




class WorksComments(APIView):
    def post(self,request):
        
        data = request.data
        
        user_work = data['clickedWork']
        user_id = data['userId']
        comments = data['Comments']
        user_comments = {
            
            'user_work':user_work,
            'user_id':user_id,  
            'comments':comments,
        }
        

        

        serializer = WorkscommentsSerializer(data= user_comments)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        
        else:
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class WorkCommentsView(APIView):
    def get(self,request,work_id):

        # user_work = Userwork.objects.get(pk=work_id)

        work_id = Userwork.objects.filter(pk = work_id)

        print('sdcbsdjcnkbwcwhwe')

        return Response(status=status.HTTP_200_OK)

        


       

class AppreciateWorkView(APIView):
    def post(self, request, work_id):
        work = get_object_or_404(Userwork, id=work_id)
        
        print(request.data)
        
        user_id = request.data['userId']
        user = UserAccount.objects.get(id = user_id)
        print(work,user,"dghkefgthqwfjwehfeguywefgweufgweuy just testing")

        
        # serializer = WorkAppreciationSerializer(data={'user_work': work.id, 'user_id': user.pk})
        appreciation_exists = WorkAppreciation.objects.filter(user_work=work, user_id=user).exists()

        if appreciation_exists:
            
            WorkAppreciation.objects.filter(user_work=work, user_id=user).delete()
            action = "deleted"
        else:
            
            appreciation = WorkAppreciation.objects.create(user_work=work, user_id=user)
            action = "created"
        
        
        # serializer = WorkAppreciationSerializer(appreciation)

        
        likes_count = WorkAppreciation.objects.filter(user_work=work).count()

        data = {
            'action': action,
            # 'appreciation_data': serializer.data,
            'likes_count': likes_count,
        }

        return Response(data, status=status.HTTP_200_OK)


# class WorkAppreciationView(APIView):
#     def post(self,request,work_id,user_id):
    
class PremiumMembershipView(APIView):
    def post(self, request):
        print("hereeee")
        print(request.data)


        serializer = PremiumMembership(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
    
        
        else:
            print(serializer.errors)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllPremiumMembershipsView(APIView):
    def get(self, request):
        premium_memberships = PremiumMembershipModel.objects.all()
        serializer = PremiumMembership(premium_memberships, many=True)
        return Response(serializer.data)


@api_view(['POST'])

def create_razorpay_order(request):
    print("here the",request.data)
    request_id=request.data.get("id")
    print("here giving the request_id",request_id)

    premium_selected = PremiumMembershipModel.objects.get(id=request_id)
    print("print the premium selected",premium_selected)
    

    client = razorpay.Client(auth=('rzp_test_TpsHVKhrkZuIUJ', 'OJzAGp6Vqx8yu2qgeHhz4y3o'))

    order_amount = int(premium_selected.price )*100
    order_currency = 'INR'

    order_params = { 
        'amount': order_amount,
        'currency': order_currency,
        'payment_capture': '1',
    }

    razorpay_order = client.order.create(order_params)
    order_id = razorpay_order['id']
    print("razopay",razorpay_order)

    return Response({'order_id': order_id, 'order_amount': order_amount})


class TransactionAPIView(APIView):
    
    def post(self, request):
        print("here giving theseezezzwawaw",request.data)
        userid=request.data.get("user_id")
        premiumid = request.data.get("premium_selected")
        print("####################",userid)
        print("*********************",premiumid)
        

        #request_id=request.data.get("id")
        user = UserAccount.objects.get(id = userid)
        #premium_selected = PremiumMembershipModel.objects.get(id = premiumid )

        print(userid,premiumid,"dkhjcgwkuhjgwefjhwegfkhjw  ju>>>>>>")

        data = request.data
        print("##############$$$@@@@@@@@@@@@@$$$$$$$$$$###############",user.id)
        data["user_id"] = user.id
        # data["premium_selected"] = premium_selected

        print(data,"just testing ")

        transaction_serializer = TransactionSerializer(data=data)
        print("here giving the data ",request.data)
        print("it will give the serializer seiaki==@@@@@@@@@@@@@@@@@@@@@@@@@@#########!@!##@$%%%",transaction_serializer)
        if transaction_serializer.is_valid():
            
            
            # print("here the ride request",ridid)
            
            
            
            rz_client.verify_payment_signature(
                razorpay_payment_id = transaction_serializer.validated_data.get("payment_id"),
                razorpay_order_id = transaction_serializer.validated_data.get("order_id"),
                razorpay_signature = transaction_serializer.validated_data.get("signature")
            )
            transaction_serializer.save()

            premium_user = Userprofile.objects.get(user_id = user.id)
            premium_user.premium_member = True 
            premium_user.save()

            print(premium_user)

            response = {
                "status_code": status.HTTP_201_CREATED,
                "message": "transaction created"
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
    
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": transaction_serializer.errors
            }
            print("here giving the error",transaction_serializer.errors)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        

# class TransactionAPIView(APIView):
    
#     def post(self, request):
#         print("here giving", request.data)
#         user = request.data.get("user_id")
#         print(user)
#         request_id = request.data.get("id")

#         transaction_serializer = TransactionSerializer(data=request.data)
#         print("here giving the data ", request.data)
#         print("it will give the serializer seiaki==@@@@@@@@@@@@@@@@@@@@@@@@@@#########!@!##@$%%%", transaction_serializer)
#         if transaction_serializer.is_valid():
#             print("true")
            
#             rz_client.utility.verify_payment_signature(
#                 razorpay_payment_id=transaction_serializer.validated_data.get("payment_id"),
#                 razorpay_order_id=transaction_serializer.validated_data.get("order_id"),
#                 razorpay_signature=transaction_serializer.validated_data.get("signature")
#             )
#             transaction_serializer.save()
#             response = {
#                 "status_code": status.HTTP_201_CREATED,
#                 "message": "transaction created"
#             }
#             return Response(response, status=status.HTTP_201_CREATED)
#         else:
#             response = {
#                 "status_code": status.HTTP_400_BAD_REQUEST,
#                 "message": "bad request",
#                 "error": transaction_serializer.errors
#             }
#             print("here giving the error")
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)



class FollowUserView(APIView):
    
    def post(self, request, user_account_id):
        print("here")
        print(request.data, "just testing for moreee")

        # Get the UserAccount instance to follow/unfollow
        user_to_follow = get_object_or_404(UserConnection, user_account_id=user_account_id)

        # Get the UserConnection instance for the current user (assuming you have a way to determine the current user)
        user = request.data.get('userId')
        current_user_connection = get_object_or_404(UserConnection, user_account=user)

        # Check if the user is already following, then unfollow
        if current_user_connection.follows.filter(pk=user_to_follow.pk).exists():
            current_user_connection.unfollow_user(user_to_follow)
            action = "unfollowed"
        else:
            current_user_connection.follow_user(user_to_follow)
            action = "followed"
        
        following_users = current_user_connection.follows.all()
        following_user_ids = [user.id for user in following_users]
        print(following_user_ids, "mdscghjcvhgferyfghwfvhgrqegfwhfbrjfgurjfbreufgerjfeugryfer")

        data = {
            'action': action,
            'following_users': following_user_ids
        }

        return Response(data, status=status.HTTP_200_OK)

    
    def get(self,request,user_id):
        print(request.data,"ndvewhgsfgjysehfwjfwgfyjwfwjfyurfvgeyruh")
        # user_account = request.data['userId']
        user = get_object_or_404(UserConnection,user_account = user_id)

        following_users = user.follows.all()
        following_user_ids = [user.id for user in following_users]
        print(following_user_ids,"Just testing the get method")

        data = {
            'following_users': following_user_ids
        }
        return Response(data, status=status.HTTP_200_OK)
        


# class Get_User(APIView):
#     def get(self, request, user_account_id):
#         user = get_object_or_404(UserAccount, id=user_account_id)

#         # Get all messages sent to or received by the user
#         user_messages = ChatMessage.objects.filter(
#         Q(sender=user) | Q(receiver=user)
#     ).values('sender', 'receiver').distinct()
#         senders = UserAccount.objects.filter(id__in=user_messages.values_list('sender', flat=True))
#         receivers = UserAccount.objects.filter(id__in=user_messages.values_list('receiver', flat=True))

#         # Example: Combine sender and receiver information in a list of dictionaries
#         user_messages_info = [
#             {'sender': sender.id,  'receiver': receiver.id}
#             for sender, receiver in zip(senders, receivers)
#         ]
#         # user_messages_info = {(sender.id, receiver.id) for sender, receiver in zip(senders, receivers)}
#         print(user_messages_info,'vegerferbfreghjfgrfhjgkwbfjhkrefgurykfgryeufhjbrekfgreuyf')
#         serializer = ChatMessageSerializer(user_messages_info, many=True)
#         return Response(serializer.data)
    
class Get_User(APIView):
    def get(self, request, user_account_id):
        user = get_object_or_404(UserAccount, id=user_account_id)

        # Get the sender and receiver information for all messages sent to or received by the user
        user_messages = ChatMessage.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).values('sender', 'receiver').distinct()

        
        user_ids = list(set(user_messages.values_list('sender', flat=True)) | set(user_messages.values_list('receiver', flat=True)))

        # just before hosing
        user_ids.remove(user.id)

        # Fetch the UserAccount instances for the remaining user IDs
        other_users = UserAccount.objects.filter(id__in=user_ids)
       
        print(other_users,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        


        # Serialize the other_users and return as a response

        # for user_id in all_user_ids:
        serializer = UserMessageprofileSerializer(other_users, many=True)
            
       
        
        return Response(serializer.data)
    


class FollowWorksPostedView(APIView):
    
    def get(self, request,user_id):
        
        # user_id = request.data['userId']

        user_id = get_object_or_404(UserConnection, pk=user_id)
        
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        
        print(user_id,'svghjgfyrefbergferjbg')

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

       
    
        following_users = user_id.user_connections.all()

        

        user_works = Userwork.objects.filter(user__in=following_users, is_verified=True)

        

        serializer = UserWorksSerializer(user_works, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class JobPosting(APIView):

    def post(self,request,user_id):

        print(">>>>>>>>>>>>>>>>>>")
        print(user_id)
        user = UserAccount.objects.get(id = user_id)
        data = {
            "user_id" : user_id,
            "jobcaption" : request.data['jobCaption'],
            "requirements" : request.data['requirements'],
            "experiance" : request.data['experiance'],
            "jobdescription" : request.data['JobDescription'],
        }



        print(data)

        serializer = UserJobSerializer(data = data)

        print(serializer)
        

        if serializer.is_valid():
            serializer.save()
            print("success")
            return Response(status = status.HTTP_201_CREATED)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

    def get(self, request, user_id):
        try:
            
            job_postings = Jobs.objects.filter(user_id=user_id)
            serializer = UserJobSerializer(job_postings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            


class AllJobsPosted(APIView):
    def get(self, request):
        
        job_postings = Jobs.objects.all()
        serializer = UserJobSerializer(job_postings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        



class Total(APIView):
    def get(self, request, *args, **kwargs):
        total_premium_paid = Payment.get_total_premium_paid()
        daily_premium = Payment.get_daily_premium()

        # Rest of your view logic

        data = {'total_premium_paid': total_premium_paid, 'daily_premium': daily_premium}
        return Response(data)
        
