from django.contrib import admin
from funnysociety.models import SiteUser,Friend,Status,StatusComment,Discussion,Event,Participant,DiscussionChat



# Display properties of models in admin site
class SiteUserAdmin(admin.ModelAdmin):
    list_display = ['user','gender','telephone','birthdate']

class StatusAdmin(admin.ModelAdmin):
    list_display = ['user','text','timestamp']

class FriendAdmin(admin.ModelAdmin):
    list_display = ['party1','party2','timestamp','isPendingRequest','isReceivedRequest']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['status','user','text','timestamp']

class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['user','title','content','timestamp']

class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['user','timestamp','title','content']

class DiscussionChatAdmin(admin.ModelAdmin):
    list_display = ['user','discussion','text','timestamp']


# Register your models here.
admin.site.register(SiteUser,SiteUserAdmin)
admin.site.register(Friend,FriendAdmin)
admin.site.register(Status,StatusAdmin)
admin.site.register(StatusComment,CommentAdmin)
admin.site.register(Discussion,DiscussionAdmin)
admin.site.register(DiscussionChat,DiscussionChatAdmin)
admin.site.register(Event)
admin.site.register(Participant)

