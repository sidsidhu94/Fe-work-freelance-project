from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import UserAccount,Userprofile,ChatMessage,Userwork,UserConnection
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


class ChatMessageAdmin(admin.ModelAdmin):
    list_editable = ['is_read', 'message']
    list_display = ['user_id','sender', 'receiver', 'is_read', 'message']


admin.site.register( ChatMessage,ChatMessageAdmin)

# admin.site.register(UserConnection)

class UserConnectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'followers_count', 'following_count')

    def followers_count(self, obj):
        return obj.follows.count()

    def following_count(self, obj):
        return obj.followed_by.count()

    followers_count.short_description = 'Followers Count'
    following_count.short_description = 'Following Count'

admin.site.register(UserConnection, UserConnectionAdmin)