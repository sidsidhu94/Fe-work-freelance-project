from django.http import Http404
from django.shortcuts import render
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
from django.db.models import Q,Subquery,OuterRef
import cloudinary
import cloudinary.uploader
from rest_framework import generics


import smtplib
from email.message import EmailMessage

from .models import UserAccount,Userprofile,Userwork,ChatMessage

User = UserAccount

from .serializer import  UserCreateSerializer, UserSerializer,OTPVerificationSerializer,ImageSerializer,UserprofileSerializer

from .serializer import UserWorkSerializer,WorkImageSerializer,UserWorksSerializer,MessageSerializer
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

            user = User.objects.filter(email = email).first()

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

        # urls = result['urls']

        # print(urls,".............................this")
        # urls = result.url

        # print(urls,".............................this")
        
       
        # print(user.id,"kjwefhiuwlfkhrelkjferifulherfiuehrf")

        
     

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


class UserProfileView(APIView):
    
    def get(self, request, user_id):
        
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


        print(request.data)
        

        try:
            user = UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        print(user,"hello hereeeeeee dont worry")
        
    


        
        user_work_serializer = UserWorkSerializer(data={
            'user': user.id,
            'work_description': work_description,
            'work_caption': work_caption
        })
        

        if user_work_serializer.is_valid():
            
            user_work_serializer.save()  
 
            
            
            images = request.data.get('selectedimages')
            
            for image in images:
                

                result = cloudinary.uploader.upload(image)
                
                
                work_image = result.pop('url')
                # print(work_image,".............................here")

                # print(user_work_serializer.data,"dataaaaaaaaaaaa,jdfjhbh")
                
                work_image_serializer = WorkImageSerializer(data={'user_work': user_work_serializer.instance.id, 'image': work_image})
                if work_image_serializer.is_valid():

                    work_image_serializer.save() 
                else:
                    
                    return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'User work and images uploaded successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'User work creation failed'}, status=status.HTTP_400_BAD_REQUEST)







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

class RejectWorkView(APIView):
    def post(self, request, work_id):
        try:
            user_work = Userwork.objects.get(pk=work_id)
        except Userwork.DoesNotExist:
            return Response({'error': 'Work not found'}, status=status.HTTP_404_NOT_FOUND)

        
        if not request.user.is_superuser:
            return Response({'error': 'Unauthorized to reject work'}, status=status.HTTP_403_FORBIDDEN)

        
        user_work.is_verified = False
        user_work.save()

        
        return Response({'message': 'Work rejected successfully'}, status=status.HTTP_200_OK)






class MyInbox(generics.ListAPIView):
      
      serializer_class = MessageSerializer

      def get_queryset(self):
          user_id = self.kwargs['user_id']

          print(user_id)

          messages = ChatMessage.objects.filter(
              id__in = Subquery(
                  User.objects.filter(
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
          
          return messages
      
class GetMessages(generics.ListAPIView):
    serializer_class = ChatMessage

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




2