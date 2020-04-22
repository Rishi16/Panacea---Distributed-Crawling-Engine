from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from .models import User
# from .models import Question


def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('crawl/index.html')
    context = {
        'latest_question_list': 'harsh',
    }
    return HttpResponse(template.render(context, request))

def new(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    if 'username' in request.session:
        template = loader.get_template('crawl/new.html')
        context = {
            'latest_question_list': 'harsh',
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")

def dashboard(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('crawl/dashboard.html')
    request.session.set_expiry(0)
    # all_users_list = User.objects.order_by('-created_date_db')
    all_users_obj = User.objects.all().values_list('username_db')
    # all_users_list = User.objects.order_by('-pub_date')
    all_users_list = []
    for each_tuple in all_users_obj:
        for single_user in each_tuple:
            print(single_user)
            all_users_list.append(single_user)
    if not request.POST['userid'] and not 'username' in request.session:
        return HttpResponseRedirect("/crawl/")

    elif 'username' in request.session and not request.POST['userid']:
        context = {
        'username': request.session['username'],
        'password': 'eclerx#123'
    }
        return HttpResponse('Harsh')
        return HttpResponse(template.render(context, request))
    else:
        username = request.POST['userid']
        password = request.POST['password']
        context = {
            'username': username,
            'password': password
        }
        if username in all_users_list:
            user_value = User.objects.get(username_db=username)
            if password == user_value.password_db:
                request.session['username'] = username
                return HttpResponse(template.render(context, request))
            else:
                return HttpResponseRedirect("/crawl/")
        else:
            return HttpResponseRedirect("/crawl/")
            # return HttpResponse(username)

    
