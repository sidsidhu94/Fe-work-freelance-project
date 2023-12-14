from django.db import models

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
import random

from cloudinary.models import CloudinaryField
import cloudinary
import cloudinary.uploader
from django.utils import timezone


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
    def create_superuser(self, email, firstname, lastname, password=None, **extra_fields):
        user = self.model(email=email, firstname=firstname, lastname=lastname, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

    # def create_superuser(self, email, firstname, lastname, password=None, **extra_fields):
    #     if not email:
    #         raise ValueError("The Email field must be set")
    #     email = self.normalize_email(email)
    #     user = self.model(email=email, firstname=firstname, lastname=lastname, **extra_fields)
    #     user.set_password(password)
    #     user.is_admin = True
    #     user.is_staff = True
    #     user.is_superuser = True
    #     user.is_active = True
    #     user.save(using=self._db)
    #     return user

    # def create_superuser(self, email, username, password):
    #     user = self.create_user(
    #         email=self.normalize_email(email),
    #         username=username,
    #         password=password,
    #     )
    #     user.is_admin = True
    #     user.is_staff = True
    #     user.is_superuser = True
    #     user.save(using=self._db)
    #     return user
    
class UserAccount(AbstractBaseUser, PermissionsMixin):
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

class PremiumMembership(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    Validity = models.PositiveIntegerField(choices=[(6, '6 months'), (12, '1 year'), (24, '2 years')])


    

    def __str__(self):
        return f"${self.price} - {self.Validity} months"

    objects = models.Manager()


class Userprofile(models.Model):
    user_id = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    # user_id = models.OneToOneField(UserAccount,on_delete=models.CASCADE)
    profile_pic = models.ImageField(default='https://cdn.vectorstock.com/i/1000x1000/06/18/male-avatar-profile-picture-vector-10210618.webp')
    username = models.CharField(null= False,max_length=30)
    country = models.CharField(null=False, max_length=100)
    description = models.CharField(max_length=100,null= False)
    skills = models.CharField(max_length=255,null= False)
    # premium = models.BooleanField(default=False)
    premium_member = models.BooleanField(default=False)
    
    def __str__(self):
         return self.username 
    

class Userwork(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    # user = models.ForeignKey(Userprofile,on_delete=models.CASCADE)
    work_description = models.CharField(max_length=255, null= True)
    work_caption = models.CharField(max_length=200,null=False)
    is_verified = models.BooleanField(default = False)
   
    


class Workimage(models.Model):
    user_work = models.ForeignKey(Userwork, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='work_images/')
    


    

class Workscomments(models.Model):
    user_work = models.ForeignKey(Userwork,on_delete=models.CASCADE,related_name="work_comments")
    user_id = models.ForeignKey(UserAccount,on_delete=models.CASCADE,related_name="user")
    comments  = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)


   
    
class WorkAppreciation(models.Model):
    user_work = models.ForeignKey(Userwork, on_delete=models.CASCADE)
    user_id =  models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    # likes = models.IntegerField(null=True, default=0)


class ChatMessage(models.Model):
   

    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content}"
    
    class Meta:
        ordering = ['timestamp']
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



# this
    

class UserConnection(models.Model):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="user_connections")
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)



    def __str__(self):
        return self.user_account.email
    
    def followers_count(self):
        return self.followed_by.count()

    def following_count(self):
        return self.followes.count()
    
    def followers_details(self):
        followers = self.follows.all()
        return {
            'count': followers.count(),
            'details': followers
        }

    def following_details(self):
        following = self.followed_by.all()
        return {
            'count': following.count(),
            'details': following
        }

    def follow_user(self, user_to_follow):
        if not self.follows.filter(pk=user_to_follow.user_account.pk).exists():
            self.follows.add(user_to_follow)
            self.save()

    def unfollow_user(self, user_to_unfollow):
        if self.follows.filter(pk=user_to_unfollow.user_account.pk).exists():
            self.follows.remove(user_to_unfollow)
            self.save()

# to this 
# class UserConnection(models.Model):
#     user_account = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name="user_connections")
#     follows = models.ManyToManyField(UserAccount, related_name="followed_by", symmetrical=False, blank=True)

#     def follow_user(self, user_to_follow):
#         if not self.follows.filter(pk=user_to_follow.user_account.pk).exists():
#             self.follows.add(user_to_follow)
#             self.save()

#     def unfollow_user(self, user_to_unfollow):
#         if self.follows.filter(pk=user_to_unfollow.user_account.pk).exists():
#             self.follows.remove(user_to_unfollow)
#             self.save()



    # def following_count(self):
    #     return self.following.count()
    

    # followers = models.IntegerField(default=0)
    # following = models.IntegerField(default=0)





class Payment(models.Model):
    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # payment_method = models.CharField(max_length=50)
    payment_status = models.BooleanField(default=False)  
    payment_id = models.CharField(max_length=255, verbose_name="Payment ID")
    order_id = models.CharField(max_length=255, verbose_name="Order ID")
    signature = models.CharField(max_length=255, verbose_name="Signature", blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    premium_selected =  models.ForeignKey(PremiumMembership,on_delete=models.CASCADE,null=True)

    def _str_(self):
        return f"Payment #{self.id} for premium #{self.Premium_id}"