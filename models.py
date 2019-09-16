# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.

#This model is common for everyone- DO NOT Edit without notifying others!
class SiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1,blank = True)
    telephone = models.CharField(max_length=10,blank = True)
    birthdate = models.DateField(null=True, blank=True)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        SiteUser.objects.create(user=instance)
    instance.siteuser.save()

#Profile models by Chathura: Only Chathura will edit
class Friend(models.Model):
    party1 = models.ForeignKey(User, unique=False, on_delete=models.CASCADE,related_name="main_party")
    party2 =models.ForeignKey(User, unique=False, on_delete=models.CASCADE,related_name="second_party")
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    isPendingRequest = models.BooleanField()
    isReceivedRequest = models.BooleanField()
        
class Status(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.CharField(max_length=999)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)

class StatusComment(models.Model):
    status = models.ForeignKey(Status,on_delete=models.CASCADE)
    user = models.ForeignKey(User, unique=False, on_delete=models.CASCADE,related_name="comment_party")
    text = models.CharField(max_length=999)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    


#Discussion models by Le:  Only Le will edit
#This is a sample table structure, modify as per your requirements
class Discussion(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    timestamp = models.TimeField(default=datetime.now, blank=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp',]

class DiscussionChat(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion,on_delete=models.CASCADE)
    text = models.CharField(max_length=999, blank=False, null=False)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)



#Events models are not used!
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    startDate = models.TimeField()
    endDate = models.TimeField()
    venue = models.CharField(max_length=500)
    timestamp = models.TimeField(default=datetime.now, blank=True)
    admin = models.ForeignKey(SiteUser,on_delete=models.CASCADE)

class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(SiteUser,on_delete=models.CASCADE)
    category=models.IntegerField()
    timestamp = models.TimeField(default=datetime.now, blank=True)
    
