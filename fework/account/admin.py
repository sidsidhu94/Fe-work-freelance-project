from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import UserAccount,Userprofile,ChatMessage,Userwork,UserConnection,Workscomments,PremiumMembership
# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('id','email','firstname','lastname','phonenumber','is_admin','is_staff')
    search_fields = ('email','firstname')
    readonly_fields = ('id','is_staff')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    ordering = ('id',) 

admin.site.register(UserAccount,AccountAdmin)

admin.site.register(Userprofile)
admin.site.register(Userwork)
admin.site.register(Workscomments)
admin.site.register(PremiumMembership)
# admin.site.register(WorkAppreciation)





class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'content')
    list_editable = ()  # If you don't want any fields to be editable in the list view

admin.site.register(ChatMessage, ChatMessageAdmin)


# class ChatMessageAdmin(admin.ModelAdmin):
#     list_editable = ['is_read', 'message']
#     list_display = ['user_id','sender', 'receiver', 'is_read', 'message']


# admin.site.register( ChatMessage,ChatMessageAdmin)

# admin.site.register(UserConnection)

# class UserConnectionAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'followers_count', 'following_count')

#     def followers_count(self, obj):
#         return obj.follows.count()

#     def following_count(self, obj):
#         return obj.followed_by.count()
    
#     # def following_count(self, obj):
#     #     return obj.following.count()

#     followers_count.short_description = 'Followers Count'
#     following_count.short_description = 'Following Count'

class UserConnectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'followers_count',  'following_count')

    def followers_count(self, obj):
        return obj.follows.count()

    def followers_details(self, obj):
        followers = obj.follows.all()
        return ", ".join([str(follower) for follower in followers])

    def following_count(self, obj):
        return obj.followed_by.count()

    def following_details(self, obj):
        following = obj.followed_by.all()
        return ", ".join([str(followee) for followee in following])

    followers_count.short_description = 'Followers Count'
    followers_details.short_description = 'Followers Details'
    following_count.short_description = 'Following Count'
    following_details.short_description = 'Following Details'


admin.site.register(UserConnection, UserConnectionAdmin)