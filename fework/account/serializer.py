from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from .models import UserAccount,Userprofile,Userwork,Workimage,ChatMessage
User = UserAccount
from django.contrib.auth import authenticate

class UserCreateSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = UserAccount
        fields = ['firstname','lastname','phonenumber','email','password','otp']

    def create(self, validated_data):
        
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance


    # def validate(self,data):
    #     user = User(**data)
    #     password = data.get('password')

    #     try:
    #         validate_password(password,user)
    #     except exceptions.ValidationError as e:
    #         serializer_errors  = serializers.as_serializer_error(e)
    #         raise exceptions.ValidationError(
    #             {'password' : serializer_errors['non_field_errors']}
    #         )
        
    #     return data

    # def create(self,**validated_data):
    #     print(validated_data)

        

    #     user =User.objects.create(
    #         firstname = validated_data['firstname'],
    #         lastname = validated_data['lastname'],
    #         email = validated_data['email'],
    #         password = validated_data['password'],
    #         phonenumber = validated_data['phonenumber'],

    #     )
        
    #     return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','firstname','lastname','email','phonenumber')


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','password']

    
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        
        try:
            user = User.objects.filter(email=email,password = password).first()

            
            
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist')

        
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid password')

        data['user'] = user  
        return data
    
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verifyotp = serializers.CharField(max_length = 6)

    

class ImageSerializer(serializers.ModelSerializer):

    profile_pic = serializers.CharField()

    class Meta: 
        model   = Userprofile
        fields  = ['user_id','profile_pic','username','country','description','skills']
        # fields  = ['id','username','country','description','skills']

# class ProfileSerializer(serializers.Serializer):



class UserprofileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    class Meta:
        model = Userprofile
        fields = ['user_id', 'profile_pic', 'username', 'country', 'description', 'skills']

    def get_profile_pic(self,obj):
        return str(obj.profile_pic)


class UserWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userwork
        fields = ['id','user', 'work_description', 'work_caption']

class WorkImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField()
    class Meta:
        model = Workimage
        fields = ['user_work', 'image']


# class WorksImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Workimage
#         fields = ('image',)

# class UserWorksSerializer(serializers.ModelSerializer):
#     images = WorksImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = Userwork
#         fields = ('work_description', 'work_caption', 'images')

# class UserAccountSerializer(serializers.ModelSerializer):
#     user_works = UserWorksSerializer(many=True, read_only=True)

#     class Meta:
#         model = UserAccount
#         fields = ('username', 'user_works')




#################

# class WorkImagesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Workimage
#         fields = ('image',)

class UserWorksSerializer(serializers.ModelSerializer):
    images = WorkImageSerializer(many=True, read_only=True)

    class Meta:
        model = Userwork
        fields = ('work_description', 'work_caption', 'is_verified', 'images','user_id')


class MessageSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    # sender = UserSerializer(read_only=True)
    # receiver = UserSerializer(read_only=True)
    # user = UserprofileSerializer(read_only=True)
    sender_profile = UserprofileSerializer(read_only=True)
    receiver_profile = UserprofileSerializer(read_only=True)
    # receiver_profile = UserSerializer(read_only = True)
    # sender_profile = UserSerializer(read_only = True)
    class Meta:
        model = ChatMessage
        fields = ['id','user','sender','sender_profile','receiver','receiver_profile','message','is_read','date']


# class MessageSerializer(serializers.ModelSerializer):
#     user_id = serializers.PrimaryKeyRelatedField(read_only=True)
#     sender_profile = UserprofileSerializer(read_only=True)
#     receiver_profile = UserprofileSerializer(read_only=True)
#     message = serializers.CharField()
#     is_read = serializers.BooleanField()
#     date = serializers.DateTimeField()

#     class Meta:
#         model = ChatMessage
#         fields = ['user_id','user', 'sender','receiver','sender_profile', 'receiver_profile', 'message', 'is_read', 'date']
