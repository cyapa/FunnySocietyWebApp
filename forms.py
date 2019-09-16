from django.contrib.auth.models import User
from .models import Status, SiteUser, Discussion
from django import forms
from . import models
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError





class UserForm(forms.ModelForm):
    GENDER_CHOICES= [
    ('M', 'M'),
    ('F', 'F')
    ]

    password = forms.CharField(widget=forms.PasswordInput)
    telephone = forms.CharField(max_length=10,min_length=10,validators=[RegexValidator(r'\d{10,10}',
            'Enter only 10 digits', 'Invalid telephone number')],help_text='Enter 10 digits only')
    gender = forms.CharField(widget=forms.Select(choices=GENDER_CHOICES),help_text='Select either M or F')
    birthdate = forms.DateField(help_text='Required Format: YYYY-MM-DD')

    class Meta:
        model = User
        fields = ['username','password','email','first_name','last_name','gender','telephone','birthdate']
        help_texts = {
            'username': None
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['telephone'].required = True
        self.fields['birthdate'].required = True


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'id': 'post_txt', 
                'required': True, 
                'placeholder': 'How are you feeling...',
            })
        }

class discussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('password','is_staff','is_active','date_joined','groups','user_permissions',
        'is_superuser','last_login','username')

