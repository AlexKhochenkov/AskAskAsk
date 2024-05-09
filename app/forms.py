from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
import pytz
from django.forms import ImageField

from app.models import Question, Answer, Tag, Profile, Upvote
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(min_length=4, widget=forms.PasswordInput)

    def clean_password(self):
        data = self.cleaned_data['password']
        if data == 'wrongpass':
            raise ValidationError('Wrong password')
        return data
    
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username','email','password']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_birth_date(self):
        data = self.cleaned_data['birth_date']
        date_as_datetime = datetime.combine(data, datetime.min.time())
        ptimezone = pytz.timezone('UTC')  # e.g., 'UTC' or 'America/New_York' 
        date_as_datetime = ptimezone.localize(date_as_datetime)
        if date_as_datetime >= timezone.now():
            raise ValidationError('Please, enter valid birth date')
        return data

    def clean(self):
        cleaned_data = super().clean()
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']

        if password and password_check and password != password_check:
            raise ValidationError("Passwords don't match")

        return cleaned_data
    
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        profile=Profile.objects.create(
            user=user,
            birth_date=self.cleaned_data['birth_date'],
            date_registrated=timezone.now()
        )
        profile.save()
        return user

class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['birth_date']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean_birth_date(self):
        data = self.cleaned_data['birth_date']
        date_as_datetime = datetime.combine(data, datetime.min.time())
        ptimezone = pytz.timezone('UTC')  # e.g., 'UTC' or 'America/New_York' 
        date_as_datetime = ptimezone.localize(date_as_datetime)
        if date_as_datetime >= timezone.now():
            raise ValidationError('Please, enter valid birth date')
        return data
    
    def save(self):
        profile = Profile.objects.get(user=self.request.user)
        profile.birth_date=self.cleaned_data['birth_date']
        recieved_avatar= self.cleaned_data.get('avatar')
        if recieved_avatar:
            profile.avatar = recieved_avatar
        profile.save()
        return profile

class SettingsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username','email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SettingsForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        data=self.cleaned_data['username']
        if User.objects.filter(username=data).exists() and data!=self.request.user.username:
            raise ValidationError("This name alredy exists")
        return data
    
    def clean_email(self):
        data=self.cleaned_data['email']
        if User.objects.filter(email=data).exists() and data!=self.request.user.email:
            raise ValidationError("This email alredy exists")
        return data
    
    def save(self):
        user = self.request.user
        user.username=self.cleaned_data['username']
        user.email=self.cleaned_data['email']
        user.save()
        return user
    
class AnswerForm(forms.ModelForm): 
    content = forms.CharField(max_length=300, required=True, widget=forms.Textarea(attrs={'rows': 5})) 
 
    def __init__(self, question, *args, **kwargs): 
        self.question = question 
        self.request = kwargs.pop('request', None) 
        super(AnswerForm, self).__init__(*args, **kwargs) 
 
    class Meta: 
        model = Answer 
        fields = ['content'] 
 
    def save(self, commit=True): 
        answer = super().save(commit=False) 
 
        # Set the profile to the current user's profile 
        answer.user = self.request.user
        answer.question = self.question 
 
        # Set the publication_date to the current date and time 
        answer.date_written = timezone.now() 
 
        if commit: 
            answer.save() 
 
        return answer
    
class AskForm(forms.ModelForm):
    tags = forms.CharField(max_length=150, required=True, widget=forms.Textarea(attrs={'rows': 2}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Retrieve and store the request object
        super(AskForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags')
        if isinstance(raw_tags, list):
            return raw_tags
        print(raw_tags)
        tags = [tag.strip() for tag in raw_tags.split(',')]
        new_tags=[]
        for tag_name in tags:
            try:
                tag = Tag.objects.get(name=tag_name)
                new_tags.append(tag)
            except Tag.DoesNotExist:
                raise ValidationError("Tag doesn't exist")
        return new_tags

    def save(self, commit=True):
        question = super().save(commit=False)

        # Set the profile to the current user's profile
        question.user = self.request.user

        # Set the publication_date to the current date and time
        question.date_written = timezone.now()

        # Set the tags
        tags = self.clean_tags()

        if commit:
            question.save()

        question.tags.set(tags)
        return question