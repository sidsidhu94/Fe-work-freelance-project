from django.db import models

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import random

from cloudinary.models import CloudinaryField
import cloudinary
import cloudinary.uploader

# Create your models here.

class UserAccountManager(BaseUserManager):
    # def create_user(self,firstname,lastname,phonenumber,email, password= None):
        # if not email:
        #         raise ValueError("Users must have an email address")
        # # if not firstname:
        # #     raise ValueError("Users must have a firstname")
        
        # # if not lastname:
        # #     raise ValueError("Users must have a lastname")
    def create_user(self, email, lastname,firstname, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, firstname=firstname,lastname = lastname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
        # user = self.model(
        #     email=self.normalize_email(email),
        #     firstname = firstname,  # Set the firstname field
        #     lastname = lastname,
        #     phonenumber = phonenumber
        # )
        # user.set_password(password)
        # user.save(using=self._db)

        # return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class UserAccount(AbstractBaseUser):
    # id = models.IntegerField(primary_key = True)
    username  = models.CharField(max_length=50,null= True)
    firstname  = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(unique=True,max_length=255)
    phonenumber = models.CharField(max_length=20,null=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    otp = models.CharField(max_length=100, null= True, blank=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname','lastname']

    def __str__(self):
         return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True


class Userprofile(models.Model):
    user_id = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    
    profile_pic = models.ImageField(default='https://cdn.vectorstock.com/i/1000x1000/06/18/male-avatar-profile-picture-vector-10210618.webp')
    username = models.CharField(null= False,max_length=30)
    country = models.CharField(null=False, max_length=100)
    description = models.CharField(max_length=100,null= False)
    skills = models.CharField(max_length=255,null= False)
    
    def __str__(self):
         return self.username 
    

class Userwork(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    work_description = models.CharField(max_length=255, null= True)
    work_caption = models.CharField(max_length=200,null=False)
    is_verified = models.BooleanField(default = False)


class Workimage(models.Model):
    user_work = models.ForeignKey(Userwork, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='work_images/')


class ChatMessage(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name="user")
    sender = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name="sender")
    receiver = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, related_name="receiver")

    message = models.CharField(max_length=1000)

    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
        verbose_name_plural = "Message"

    def __str__(self):
        return f"{self.sender} - {self.receiver}"

    @property
    def sender_profile(self):
        return self.sender.userprofile
    
    @property
    def receiver_profile(self):
        return self.receiver.userprofile
    

    # def sender_profile(self):
    #     sender_profile = UserAccount.objects.get(user=self.sender)
    #     return sender_profile
    # @property
    # def receiver_profile(self):
    #     receiver_profile = UserAccount.objects.get(user=self.receiver)
    #     return receiver_profile



    

class UserConnection(models.Model):
    user_account = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name="user_connections")
    follows = models.ManyToManyField("self",
                                     related_name= "followed_by",
                                     symmetrical=False,
                                     blank=True)
    
    def __str__(self):
        return self.user_account.email
    
    def followers_count(self):
        return self.follows.count()

    def following_count(self):
        return self.followed_by.count()
    

    # followers = models.IntegerField(default=0)
    # following = models.IntegerField(default=0)
    # appreciation = models.IntegerField(default=0)




class Workscomments(models.Model):
    user_work = models.ForeignKey(Userwork,on_delete=models.CASCADE,related_name="work_comments")
    comments  = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)



