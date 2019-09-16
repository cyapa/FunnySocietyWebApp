from django.shortcuts import render, redirect,reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import UserForm, EditProfileForm
from django.forms.models import inlineformset_factory
from django.contrib import messages
from .forms import StatusForm
from .models import Status, SiteUser,Friend,StatusComment, Discussion,DiscussionChat
from django.views.decorators.http import require_http_methods
from django.http import Http404,JsonResponse,HttpResponse,HttpResponseRedirect
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
import json
from itertools import chain

#User related views
class UserFormView(View):
    form_class = UserForm
    template_name ='registration/registration_form.html'

    #Registration display form
    def get(self,request):
        form= self.form_class(None)
        return render(request,self.template_name,{'form': form})

    #On registration form submit, add users to database
    def post(self,request):

        form = self.form_class(data=request.POST)
        
        if form.is_valid():
            user=form.save()
            user.refresh_from_db()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.siteuser.telephone = form.cleaned_data.get('telephone')
            user.siteuser.gender = form.cleaned_data.get('gender')
            user.siteuser.birthdate = form.cleaned_data.get('birthdate')
            user.save()
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request,user)
                return redirect('profile')
            else:
                return HttpResponse("<h1>User is not active!</h1>")
        else:
            return HttpResponse("<h1>Not registered!</h1>")

#To Change your profile
@login_required
def edit_profile(request,pk):
    user = User.objects.get(pk=pk)
    user_form = EditProfileForm(instance=user)

    ProfileInlineFormset = inlineformset_factory(User, SiteUser, fields=('gender', 'telephone', 'birthdate'))
    formset = ProfileInlineFormset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = EditProfileForm(request.POST, request.FILES, instance=user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()

        return render(request, "profile/edit_profile.html", {
            "noodle": pk,
            "noodle_form": user_form,
            "formset": formset,
        })
    else:
        raise PermissionDenied
#------End of user views-------------------


# To create user discussion
def create_discussion(request):
    if request.method == 'POST':
        post_title = request.POST.get('title')
        post_content = request.POST.get('content')
        post = Discussion.objects.create(title=post_title,content=post_content,user=request.user)
        post.save()
        return redirect('profile')
    
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "invalid request"}),
            content_type="application/json"
        )
#To get user discussion
def get_discussion(request,username=None):
    if request.method == 'GET':

        query_user = request.user
        if username is not None:
            query_user=User.objects.get(username=username)

        admin_discussion_list = Discussion.objects.filter(user=query_user).values('id','content', 'title','timestamp') 
        chat_discussion_ids= DiscussionChat.objects.filter(user=query_user).distinct().values('discussion')
        
        my_discussion_list = Discussion.objects.filter(id__in=chat_discussion_ids).values('id','content', 'title','timestamp') 
   

        discussions = list(my_discussion_list | admin_discussion_list )
        #context = locals()
        #x= list(context)
        return JsonResponse(discussions, safe=False)

    else:
        return JsonResponse('', safe=False)   

#To get  discussion page
def discussion_page(request,pk):
    is_admin = False
    try:
        discussion = Discussion.objects.get(pk=pk)
        if  request.user == discussion.user:
            is_admin = True
    except:
        raise Http404("User does not exist")
    template = "discussion_page.html"

    context = locals()
    return render(request, template,context )   

#Delete a discussion
def delete_discussion(request,pk=0):
    if request.method == 'POST':
        discussion_id = request.POST.get('id')
        Discussion.objects.filter(id=discussion_id).delete()
        return redirect('profile')

# To post user status
def create_post(request):
    if request.method == 'POST':
        post_text = request.POST.get('the_post')
        post = Status.objects.create(text=post_text,user=request.user)
        post.save()
        return redirect('profile')
    
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

#To get user status
def get_status(request,username=None):
    if request.method == 'GET':

        query_user = request.user
        if username is not None:
            query_user=User.objects.get(username=username)

        statusList = Status.objects.all().filter(user=query_user).values('id','text', 'timestamp').order_by('-timestamp') 
        status_list = list(statusList)
        return JsonResponse(status_list, safe=False)

    else:
        return JsonResponse('', safe=False)

# To post a comment
def post_comment(request,username=None):
    if request.method == 'POST':
        status_id = request.POST.get('status_id')
        comment_txt = request.POST.get('comment_txt')
        status = Status.objects.get(id=status_id)
        request = StatusComment.objects.create(status=status,user=request.user,text=comment_txt)
        return HttpResponse(
            json.dumps({"status": "comment_added"}),
            content_type="application/json"
            )

# Get all comments of the provided user
def get_comments(request,username=None):
    if request.method == 'GET':
        query_user = request.user
        if username is not None:
            query_user=User.objects.get(username=username)

        status_list = Status.objects.filter(Q(user=query_user))
        comments = StatusComment.objects.all().filter(status__in=status_list).values('status_id','id','user__first_name','text', 'timestamp')
        comment_list = list(comments)
        return JsonResponse(comment_list, safe=False)

#To search friend/discussion
def search(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        if q:
            users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q)| Q(last_name__icontains=q))
            discussions = Discussion.objects.filter(Q(title__icontains=q))
            if users:
                return render(request, 'search.html', {'users': users, 'query': q})
            elif discussions:
                return render(request, 'search.html', {'discussions': discussions, 'query': q})
            else:
                messages.error(request,'Results Not Found')
        else:
            return HttpResponseRedirect('profile')
    return render(request, 'search.html', {'messages': 'Results Not Found'})    
  

  # Friend List Page

#To profile friend
def profile_friend(request,username):
     # If no such user exists raise 404
    try:
        user = User.objects.get(username=username)
    except:
        raise Http404("User does not exist")

    # Flag that determines if we should show editable elements in template
    editable = False
    # Handling non authenticated user
    if request.user.is_authenticated and request.user == user:
        editable = True

    #If user is not a friend hide private data
    try:
        oldFriendMain = Friend.objects.get(party1=user,party2=request.user.id,isPendingRequest=False)
    except Friend.DoesNotExist:
        oldFriendMain = None

    try:
        oldFriendSecond = Friend.objects.get(party2=user,party1=request.user.id,isPendingRequest=False)
    except Friend.DoesNotExist:
        oldFriendSecond = None
    
    #Not a current firend
    if request.user != user and oldFriendMain is None and oldFriendSecond is None:
        user.siteuser.birthdate = ""
        user.siteuser.telephone = ""
    else:
        status_list = Status.objects.filter(Q(user=user))
    
    context = locals()
    return render(request, "profile/profile_friend.html", context)

#Get all friends
def friend_list(request,username):
     # If no such user exists raise 404
    user = User.objects.get(username=username)
    friend_List = Friend.objects.filter(Q(party1=user) | Q(party2=user))
    data = []
    for friend in friend_List:
        cur_user = User.objects.get(id=request.user.id)
        responseData = {
            'friend': list(User.objects.filter(id=friend.party1.id).values('id','username'))if cur_user.id != friend.party1.id else list(User.objects.filter(id=friend.party2.id).values('id','username')),
        }
        data.append(responseData)
    template = 'friend_list.html'    
    return render(request, template, {'data':data})

#To add friend
def add_friend(request):
    if request.method == 'POST':
        requestUsername = request.POST.get('username')

        try:
            newFriend = User.objects.get(username=requestUsername)
        except User.DoesNotExist:
            newFriend = None

        #Check same user or not
        if newFriend == request.user:
            return HttpResponse(
            json.dumps({"status": "same_user"}),
            content_type="application/json"
        )


        #Check user availability
        if newFriend is None:
            return HttpResponse(
            json.dumps({"status": "user_not_found"}),
            content_type="application/json"
        )

        #Check user is a friend already
        try:
            oldFriendMain = Friend.objects.get(party1=newFriend,party2=request.user.id)
        except Friend.DoesNotExist:
            oldFriendMain = None

        try:
            oldFriendSecond = Friend.objects.get(party2=newFriend,party1=request.user.id)
        except Friend.DoesNotExist:
            oldFriendSecond = None


        if oldFriendMain is None and oldFriendSecond is None:
            request = Friend.objects.create(party1=request.user,party2=newFriend,isPendingRequest=True,isReceivedRequest=False)
            return HttpResponse(
                json.dumps({"status": "request_sent"}),
                content_type="application/json"
            )
        return HttpResponse(
            json.dumps({"status": "already_sent"}),
            content_type="application/json"
        )

#To get friends
def get_friends(request):
    if request.method == 'GET':
         
        friend_List = Friend.objects.filter(Q(party1=request.user) | Q(party2=request.user))
        data = []
        for friend in friend_List:

            cur_user = User.objects.get(id=request.user.id) #get current user's username
     

            responseData = {
                'friend': list(User.objects.filter(id=friend.party1.id).values('id','first_name','last_name','username')) if cur_user.id != friend.party1.id else list(User.objects.filter(id=friend.party2.id).values('id','first_name','last_name','username')),
                'timestamp': friend.timestamp,
                'isPendingRequest':friend.isPendingRequest,
                'isReceivedRequest': friend.isReceivedRequest if cur_user.id == friend.party1.id else not friend.isReceivedRequest
            }

            data.append(responseData)
        return JsonResponse(data,safe=False)

#Accept a new friend
def accept_friend(request):
    if request.method == 'POST':
        new_friend_id = request.POST.get('friend_id')
        newFriend = User.objects.get(pk=new_friend_id)
        try:
            request = Friend.objects.filter(Q(party1=newFriend) & Q(party2=request.user)).update(isPendingRequest=False)
            return HttpResponse(
                json.dumps({"status": "friend_accepted"}),
                content_type="application/json"
            )
        except:
            return HttpResponse(
                json.dumps({"status": "error"}),
                content_type="application/json"
            )

#Decline a friend request
def decline_friend(request):
    if request.method == 'POST':
        new_friend_id = request.POST.get('friend_id')
        newFriend = User.objects.get(pk=new_friend_id)

        try:
            request = Friend.objects.filter(Q(party1=newFriend) & Q(party2=request.user)).get()
            request.delete()
            return HttpResponse(
                json.dumps({"status": "friend_declined"}),
                content_type="application/json"
            )

        except:
            return HttpResponse(
                json.dumps({"status": "error"}),
                 content_type="application/json"
            )

#Delete a friend request
def delete_friend_request(request):
    if request.method == 'POST':
        new_friend_id = request.POST.get('friend_id')
        newFriend = User.objects.get(pk=new_friend_id)

        try:
            request = Friend.objects.filter(Q(party2=newFriend) & Q(party1=request.user)).get()
            request.delete()
            return HttpResponse(
                json.dumps({"status": "friend_declined"}),
                content_type="application/json"
            )

        except:
            return HttpResponse(
                json.dumps({"status": "error"}),
                 content_type="application/json"
            )

#Delete a current friend
def delete_friend(request):
    if request.method == 'POST':
        new_friend_id = request.POST.get('friend_id')
        newFriend = User.objects.get(pk=new_friend_id)

        try:
            request = Friend.objects.filter(Q(party2=newFriend) & Q(party1=request.user)).get()
            request.delete()
            return HttpResponse(
                json.dumps({"status": "friend_deleted"}),
                content_type="application/json"
            )

        except:
            try:
                request = Friend.objects.filter(Q(party1=newFriend) & Q(party2=request.user)).get()
                request.delete()
                return HttpResponse(
                    json.dumps({"status": "friend_deleted"}),
                    content_type="application/json"
                )
            except:

                return HttpResponse(
                     json.dumps({"status": "error"}),
                     content_type="application/json"
                 )

#Post chat in discussion
def post_chat(request,pk=0):
    if request.method == "POST":
        chat_text = request.POST.get('chat_text')
        discussion = Discussion.objects.get(pk=pk)

        chat = DiscussionChat.objects.create(user=request.user,discussion=discussion,text=chat_text)
        chat.save()
        
    return HttpResponse(
        json.dumps({"status": "chat_added"}),
        content_type="application/json"
        )

#Load chats for a discusison
def load_chat(request,pk=0):
    if request.method == 'GET':
        discussion_id = request.POST.get('chat_text')
        discussion = Discussion.objects.get(pk=pk)

    chats = DiscussionChat.objects.all().filter(discussion=discussion).order_by('timestamp')
    
    chat_data = []
    for chat in chats:
        discussion = Discussion.objects.get(pk=chat.discussion.id)
        responseData = {
                'chat_id': chat.id,
                'timestamp':  chat.timestamp,
                'first_name': chat.user.first_name,
                'text':chat.text,
                'is_owner': True if request.user == chat.user or ( discussion.user == request.user) else False
            }
        chat_data.append(responseData)

    return JsonResponse(chat_data, safe=False)

#Delete a chat
def delete_chat(request,pk=0):
    if request.method == 'POST':
        chat_id = request.POST.get('id')
        DiscussionChat.objects.filter(id=chat_id).delete()
        return redirect('profile')


# Get all discussions
def discussion_list(request):
    discussions = Discussion.objects.all().order_by('-timestamp') 
    template = "discussion_list.html"
    return render(request, template, {'discussions': discussions})
