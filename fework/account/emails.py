from django.core.mail import send_mail

import random
from django.conf import settings
from .models import UserAccount


# def sent_otp_via_email(email,otp):
#     subject = "your account verification email"
    
#     message = f'Your otp is {otp}'
#     email_from = settings.EMAIL_HOST
#     send_mail(subject , message , email_from , [email])
    
    