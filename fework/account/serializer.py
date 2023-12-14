from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from .models import UserAccount,Userprofile,Userwork,Workimage,ChatMessage,UserConnection,Workscomments,WorkAppreciation,PremiumMembership, Payment

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
        fields = "__all__"


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

# class ProfileSerializer(serializers.Serializer):f



class UserprofileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    
    class Meta:
        model = Userprofile
        fields = ['user_id','profile_pic', 'username', 'country', 'description', 'skills']

    def get_profile_pic(self,obj):
        return str(obj.profile_pic)


class UserWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userwork
        fields = ['id','user', 'work_description', 'work_caption','is_verified']

class WorkImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField()
    class Meta:
        model = Workimage
        fields = ['user_work', 'image']

class WorkImagesSerializer(serializers.ModelSerializer):
    image = serializers.CharField()
    class Meta:
        model = Workimage
        fields = ['image']



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
# /////////////////////////// comments  ///////////////////////// #



class WorkscommentsSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = Workscomments
        fields = ('user_work','user_id','comments','date','user_profile')

    def get_user_profile(self, obj):
        user_profile = Userprofile.objects.get(user_id=obj.user_id)
        serializer = UserprofileSerializer(user_profile)
        return serializer.data

    




# /////////////////////////// comments  ///////////////////////// #

# class WorkImagesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Workimage
#         fields = ('image',)

class UserWorksSerializer(serializers.ModelSerializer):
    images = WorkImagesSerializer(many=True, read_only=True)
    # profile = UserprofileSerializer(source='user',read_only = True)
    user_profile = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    work_appreciation =  serializers.SerializerMethodField()
    # comments = WorkscommentsSerializer(source= 'ChatMessage',read_only = True )
    


    class Meta:
        model = Userwork
        
        fields = ('id','work_description', 'work_caption', 'is_verified', 'images','user_id','user_profile','comments','work_appreciation')
        # fields = '__all__'
    
    def get_user_profile(self, obj):
        user_profile = Userprofile.objects.get(user_id=obj.user_id)
        serializer = UserprofileSerializer(user_profile)
        return serializer.data
    
    def get_comments(self, obj):
        comments = Workscomments.objects.filter(user_work_id=obj).order_by('-date')
        serializer = WorkscommentsSerializer(comments, many=True)
        return serializer.data
    
    def get_work_appreciation(self, obj):
        appreciation = WorkAppreciation.objects.filter(user_work=obj)
        serializer = WorkAppreciationSerializer(appreciation, many=True)
        return serializer.data
    
    
    

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
        fields = ['id','user','sender','sender_profile','receiver','receiver_profile','content','is_read','date']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_profile = serializers.SerializerMethodField()
    receiver_profile = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp','sender_profile','receiver_profile']

    def get_sender_profile(self, obj):
        sender_profile = Userprofile.objects.get(user_id=obj.sender_id)
        serializer = UserprofileSerializer(sender_profile)
        return serializer.data
    
    def get_receiver_profile(self, obj):
        receiver_profile = Userprofile.objects.get(user_id=obj.receiver_id)
        serializer = UserprofileSerializer(receiver_profile)
        return serializer.data


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


class UserConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConnection
        # fields = ['id', 'user_account', 'follows', 'followed_by']

        fields = '__all__'



class UserprofilesSerializer(serializers.ModelSerializer):
    user_works = UserWorksSerializer(many=True, read_only=True)
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Userprofile
        fields = ('user_id', 'profile_pic', 'username', 'country', 'description', 'skills', 'user_works')

    def get_profile_pic(self,obj):
        return str(obj.profile_pic)
    


# /////////////////////////// following ////////////////////////////


class UserConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConnection
        fields = '__all__'


# class UserConnectionSerializer(serializers.ModelSerializer):
    # followers = serializers.SerializerMethodField()
    # following = serializers.SerializerMethodField()

    # class Meta:
    #     model = UserConnection
    #     fields = ('id', 'user_account', 'followers', 'following')

    # def get_followers(self, obj):
    #     followers = obj.follows.all()
    #     return {
    #         'count': followers.count(),
    #         'details': [{'user_account_id': follower.user_account.id, 'email': follower.user_account.email} for follower in followers]
    #     }

    # def get_following(self, obj):
    #     following = obj.followed_by.all()
    #     return {
    #         'count': following.count(),
    #         'details': [{'user_account_id': followed.user_account.id, 'email': followed.user_account.email} for followed in following]
    #     }


# /////////////////////////// following ////////////////////////////

from rest_framework import serializers
from .models import UserConnection

class UserConnectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserConnection
        fields = '__all__'



class WorkAppreciationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAppreciation
        fields = "__all__"

class PremiumMembership(serializers.ModelSerializer):
    
    class Meta:
        model = PremiumMembership
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):

    # userdetail = UserSerializer("user_id")
    # premium_detail = PremiumMembership("premium_selected")

    
    class Meta:
        model = Payment
        # fields = ["user_id","userdetail","amount","payment_status","payment_id","order_id","signature","timestamp","premium_selected","premium_detail"]
        fields = "__all__"

class UserMessageprofileSerializer(serializers.ModelSerializer):
    # profile_pic = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount  # Update to your actual model name
        fields = ['user_id','user_profile']

    # def get_profile_pic(self, obj):
    #     return str(obj.profile_pic)

    def get_user_id(self, obj):
        return str(obj.id)
    
    def get_user_profile(self, obj):
        user_profile = Userprofile.objects.get(user_id=obj.id)
        serializer = UserprofileSerializer(user_profile)
        return serializer.data