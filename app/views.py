import jwt
import time
import json
from datetime import datetime
from cent import Client
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
import math
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from app.forms import LoginForm, RegisterForm, SettingsForm, ProfileForm, AnswerForm, AskForm
from .models import User
from .models import Question, Answer, Tag, Profile, Upvote
from django.core.cache import cache

from django.conf import settings as conf_settings

# Create your views here.
# TAGS = [
#     {'name': 'python', 'color': 'bg-primary'},
#     {'name': 'mySQL', 'color': 'bg-danger'},
#     {'name': 'django', 'color': 'bg-warning'},
#     {'name': 'java', 'color': 'bg-secondary'},
#     {'name': 'css', 'color': 'bg-success'}
# ]

# QUESTIONS = [
#     {
#         'id':i,
#         'title': f'Question {i}',
#         'content': f'Long lorem ipsun {i}',
#         'upvotes': i%10,
#         'tags': [TAGS[i%5]['name'], TAGS[(i+2)%5]['name']]
#     } for i in range(100)
# ]

# ANSWERS = [
#     {
#         'id':i,
#         'content' : f'My beautiful answer {i}',
#         'upvotes': i%10
#     } for i in range(50)
# ]

# def user_sorter():
#     users=User.objects.annotate(
#         raiting=Sum('questions__upvotes__vote')+Sum('answers__upvotes__vote')
#     )
#     return users.order_by('-raiting')[:5]

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeEncoder, self).default(o)
    
def cache_tags():
    cache_key = 'popular_tags'
    tags = [{"id": tag.id, "name": tag.name, "question_num": tag.question_num} for tag in Tag.objects.hot()]
    cache.set(cache_key, tags, 60)

def tag_hot():
    cache_key = 'popular_tags'
    tags = cache.get(cache_key)
    if not tags:
        cache_tags()
    return {"tags": tags}

def cache_users():
    cache_key = 'best_users'
    users = [{"username": profile.user.username} for profile in Profile.objects.best_users()]
    cache.set(cache_key, users, 60)

def user_best():
    cache_key = 'best_users'
    users = cache.get(cache_key)
    if not users:
        cache_users()
    return {"best_users": users}

client = Client(conf_settings.CENTRIFUGO_API_URL, api_key=conf_settings.CENTRIFUGO_API_KEY, timeout=1)

def get_centrifugo_data(user_id, channel):
    token = jwt.encode({"sub": str(user_id), "exp": int(time.time()) + 10*60}, conf_settings.CENTRIFUGO_TOKEN_HMAC_SECRET, algorithm="HS256")
    return {
        "centrifugo": {
            "token": token,
            "ws_url": conf_settings.CENTRIFUGO_WS_URL,
            "channel": channel
        }
    }

def paginate(request, objects, per_page=2):
    limit=math.ceil(len(objects)/per_page)
    paginator = Paginator(objects, per_page)

    page = request.GET.get('page', 1)
    try:
        if int(page)>limit or int(page)<=0:
            return {'content': paginator.page(1), 'page': int(page), 'limit': limit}
        return {'content': paginator.page(page), 'page': int(page), 'limit': limit}
    except ValueError:
        return {'content': paginator.page(1), 'page': int(page), 'limit': limit}

def index(request):
    page_params = paginate(request, Question.objects.recent())
    print(page_params['page'])
    return render(request, "index.html", 
                  {'questions': page_params['content'], 
                   **tag_hot(),
                   **user_best(), 
                   'page': page_params['page'], 
                   'prev_page': page_params['page']-1, 
                   'fol_page': page_params['page']+1,
                   'limit': page_params['limit']})


def tag(request, tag_name):
    items=Question.objects.tag(tag_name)
    page_params=paginate(request, items)
    return render(request, "tag.html", 
                    {'questions': page_params['content'], 
                   **tag_hot(),
                   **user_best(), 
                   'page': page_params['page'], 
                   'prev_page': page_params['page']-1, 
                   'fol_page': page_params['page']+1,
                   'limit': page_params['limit'], 
                    'tag': tag_name})

def hot(request):
    items=Question.objects.hot()
    page_params=paginate(request, items)
    return render(request, "hot.html", 
                    {'questions': page_params['content'], 
                   **tag_hot(),
                   **user_best(), 
                   'page': page_params['page'], 
                   'prev_page': page_params['page']-1, 
                   'fol_page': page_params['page']+1,
                   'limit': page_params['limit']})

@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def question(request, question_id):

    token = jwt.encode({"sub": "42", "exp": int(time.time()) + 10*60}, "secret", algorithm="HS256")

    print(token)
    item = Question.objects.get(id=question_id)
    if request.method == 'GET':
        answer_form = AnswerForm(question=item)
    if request.method == 'POST':

        answer_form = AnswerForm(request=request, question=item, data=request.POST)
        if answer_form.is_valid():
            answer = answer_form.save()

            if answer:
                client.publish(f'question.{question_id}', json.loads(json.dumps(model_to_dict(answer), cls=DateTimeEncoder)))

                page_params = paginate(request, Answer.objects.hot(question_id), 2)
                index=0
                oldanswer=None
                page_number=1
                for item in page_params['content']:
                    if item == answer:
                        page_number = 1+index//2
                        break
                    index+=1
                    oldanswer=item
                if index%2==0:
                    url = f"{reverse('question', args=[question_id])}?page={page_number}"
                else:
                    url = f"{reverse('question', args=[question_id])}?page={page_number}#{oldanswer.id}"
                return redirect(url)

            else:
                answer_form.add_error(field=None, error="Answer saving error")
    page_params=paginate(request, Answer.objects.hot(question_id))
    return render(request, "question.html", 
                    {'question': item,
                     'form': answer_form,
                    'answers': page_params['content'], 
                   **tag_hot(),
                   **user_best(), 
                   'page': page_params['page'], 
                   'prev_page': page_params['page']-1, 
                   'fol_page': page_params['page']+1,
                   'limit': page_params['limit'],
                   **get_centrifugo_data(request.user.id, f'question.{question_id}')})

@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def ask(request):
    if request.method == 'GET':
        ask_form = AskForm()
    if request.method == 'POST':

        ask_form = AskForm(request=request, data=request.POST)
        if ask_form.is_valid():
            question = ask_form.save()
            url = f"{reverse('question', args=[question.id])}"
            return redirect(url)
    return render(request, "ask.html" , { 
                    'form': ask_form,
                   **tag_hot(),
                   **user_best()})


@login_required
def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('continue', '/'))

@csrf_protect
def log_in(request):
    if request.user.is_authenticated:
        logout(request)
        if request.GET.get('continue')=='/settings':
            return redirect(reverse('index'))
        return redirect(request.GET.get('continue', '/'))
    if request.method=="GET":
        login_form=LoginForm()
    if request.method=="POST":
        login_form=LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('continue', '/'))
            else:
                login_form.add_error(None, "Wrong password or user doesn't exist")
                login_form.add_error("password", "")
                login_form.add_error("username", "")
    return render(request, "login.html", context={"form": login_form, **tag_hot(),
                   **user_best()})

@csrf_protect
def signup(request):
    if request.user.is_authenticated: 
        logout(request) 
 
    if request.method == 'GET': 
        profile_form = RegisterForm() 
    if request.method == 'POST': 
        profile_form = RegisterForm(request.POST) 
        if profile_form.is_valid(): 
            user = profile_form.save() 
            if user: 
                login(request, user) 
                return redirect(reverse('index')) 
            else: 
                profile_form.add_error(field=None, error="Profile saving error")
    return render(request, "signup.html", {
                    'form': profile_form, 
                   **tag_hot(),
                   **user_best()})

@csrf_protect
@login_required
def settings(request):
    user=request.user
    profile=user.profile
    if request.method == 'GET': 
        profile_form = ProfileForm(instance=profile) 
        settings_form = SettingsForm(instance=user)
    if request.method == 'POST': 
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile, request=request) 
        settings_form = SettingsForm(request.POST, instance=user, request=request)
        if profile_form.is_valid() and settings_form.is_valid(): 
            profile = profile_form.save() 
            user =settings_form.save()
            if user: 
                login(request, user)
                return redirect(reverse('settings')) 
            else: 
                profile_form.add_error(field=None, error="Profile saving error")
    return render(request, "settings.html", { 
                    'profileform': profile_form,
                    'settingsform': settings_form,
                   **tag_hot(),
                   **user_best()})

@csrf_protect
@login_required
def correct(request):
    answerid=request.POST.get('answerid')
    questionid=request.POST.get('questionid')
    answer=Answer.objects.get(id=answerid)
    question=Question.objects.get(id=questionid)
    if question.user==request.user:
        if answer.correct==False:
            answer.correct=True
            answer.save()
            return JsonResponse({'correct': 1, 'success': 1})
        else:
            answer.correct=False
            answer.save()
            return JsonResponse({'correct': 0, 'success': 1})
    else:
        return JsonResponse({'success': 0})

@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def like(request):
    id=request.POST.get('id')
    type=request.POST.get('type')
    vote=request.POST.get('vote')
    if vote=='0':
        if type=='question':
            question = get_object_or_404(Question, id=id)
            liked=Upvote.objects.is_liked(user=request.user, content_object=question)
            return JsonResponse({'liked':liked})
        else:
            answer = get_object_or_404(Answer, id=id)
            liked=Upvote.objects.is_liked(user=request.user, content_object=answer)
            return JsonResponse({'liked':liked})
    if type=='question':
        question = get_object_or_404(Question, id=id)
        Upvote.objects.toggle_like(user=request.user, content_object=question, vote=int(vote))
        count=Question.objects.get_likes(id)
        liked=Upvote.objects.is_liked(user=request.user, content_object=question)
    else:
        answer = get_object_or_404(Answer, id=id)
        Upvote.objects.toggle_like(user=request.user, content_object=answer, vote=int(vote))
        liked=Upvote.objects.is_liked(user=request.user, content_object=answer)
        count=Answer.objects.get_likes(id)
    return JsonResponse({'count':count, 'liked':liked})
