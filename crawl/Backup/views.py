from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from .models import User, db_batch
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render
from .tasks import schedule_batch
from crawl.forms import db_batchForm, db_scriptForm

# from .models import Question


def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    logout(request)
    template = loader.get_template('crawl/index.html')
    context = {
        'latest_question_list': 'harsh',
    }
    return HttpResponse(template.render(context, request))

def new1(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    if request.user.is_authenticated:
        template = loader.get_template('crawl/new.html')
        context = {
            'latest_question_list': 'harsh',
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")

def dashboard(request):
    # create_dir.delay('harsh')
    # # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # template = loader.get_template('crawl/dashboard.html')
    # request.session.set_expiry(0)
    # # all_users_list = User.objects.order_by('-created_date_db')
    # all_users_obj = User.objects.all().values_list('username_db')
    # # all_users_list = User.objects.order_by('-pub_date')
    # all_users_list = []
    # for each_tuple in all_users_obj:
    #     for single_user in each_tuple:
    #         print(single_user)
    #         all_users_list.append(single_user)
    # if not request.POST['userid'] and not 'username' in request.session:
    #     return HttpResponseRedirect("/crawl/")

    # elif 'username' in request.session and not request.POST['userid']:
    #     context = {
    #     'username': request.session['username'],
    #     'password': 'eclerx#123'
    # }
    #     return HttpResponse('Harsh')
    #     return HttpResponse(template.render(context, request))
    # else:
    #     username = request.POST['userid']
    #     password = request.POST['password']
    #     context = {
    #         'username': username,
    #         'password': password
    #     }
    #     if username in all_users_list:
    #         user_value = User.objects.get(username_db=username)
    #         if password == user_value.password_db:
    #             request.session['username'] = username
    #             return HttpResponse(template.render(context, request))
    #         else:
    #             return HttpResponseRedirect("/crawl/")
    #     else:
    #         return HttpResponseRedirect("/crawl/")
    #         # return HttpResponse(username)

    template = loader.get_template('crawl/dashboard.html')
    request.session.set_expiry(0)


    # Check if user has already logged in or not
    if request.user.is_authenticated:
        if request.method == "POST":
            request.session['msg_data'] = ''
            return HttpResponseRedirect("/crawl/dashboard")
        else:
            if 'msg_data' in request.session:
                if request.session['msg_data'] == 'welcome':
                    context = {
                    'username': request.session['username'],
                    'msg_to_show': 'Welcome to Panacea',
                    'detailed_message': 'Hover me to enable the Close Button. You can hide the left sidebar clicking on the button next to the logo.'
                    }
                    request.session['msg_data'] = ''
                elif request.session['msg_data'] == 'create_batch':
                    context = {
                    'username': request.session['username'],
                    'msg_to_show': request.session['batch_name'],
                    'detailed_message': 'Your batch has been created and scheduled properly. Please go to the search option to visit the batch.'
                    }
                    request.session['msg_data'] = ''
                elif request.session['msg_data'] == 'create_supplier':
                    context = {
                    'username': request.session['username'],
                    'msg_to_show': request.session['supplier_name'],
                    'detailed_message': 'Your supplier has been created/updated properly.'
                    }
                    request.session['msg_data'] = ''
                else:
                    request.session['username'] = request.user.username
                    context = {
                    'username': request.session['username'],
                    'msg_to_show': '',
                    'detailed_message': ''
                    }
                    request.session['msg_data'] = ''
                return HttpResponse(template.render(context, request))
            else:
                request.session['username'] = request.user.username
                context = {
                    'username': request.session['username'],
                    'msg_to_show': '',
                    'detailed_message': ''
                    }
                request.session['msg_data'] = ''
                return HttpResponse(template.render(context, request))

    # if user is not logged in then execution will go in else
    else:
        # Check http method for authentication
        if request.method == "POST":
            if 'userid' in request.POST and 'password' in request.POST:
                username = request.POST['userid']
                password = request.POST['password']
                user = authenticate(request, username=username, password=password)
                # If the user already exists in database
                if user is not None:
                    login(request, user)
                    context = {
                    'username': username,
                    'password': password,
                    }
                    user = User.objects.get(username=username)
                    request.session['username'] = username
                    request.session['team'] = user.team_name.team
                    request.session['user_id'] = user.id
                    request.session['email'] = user.email
                    request.session['msg_data'] = 'welcome'
                    # user = User.objects.get(username=username)
                    # user.team_name.team = 'RS'
                    # user.team_name.project = 'RS'
                    # user.save()
                    return HttpResponseRedirect("/crawl/dashboard")
                    # return HttpResponse(template.render(context, request))

                # User has entered wrong credentials
                else:
                    return HttpResponseRedirect("/crawl/")
            else:
                return HttpResponseRedirect("/crawl/")
        # if the method is not post then user will be redirected to login window
        else:
            return HttpResponseRedirect("/crawl/")

def new(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = db_batchForm(request.session['user_id'], request.session['team'], request.POST, request.FILES)
            if form.is_valid():
                # form.save()
                new_batch = form.save()
                request.session['msg_data'] = 'create_batch'
                request.session['batch_name'] = request.POST['batch_name']
                # user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                # start the task in the background
                # General Syntax -> schedule_batch.delay(teamName, batchName, inputFile, scriptName)
                schedule_batch.delay(new_batch.id, new_batch.batch_name, new_batch.team, new_batch.input_file.name, new_batch.script_name_id, request.session['user_id'])
                return HttpResponseRedirect("/crawl/dashboard")
            else:
                for i in range(0,50):
                    print(i)
        else:
            form = db_batchForm(request.session['user_id'], request.session['team'])
        return render(request, 'crawl/new.html', {
            'form': form
        })
    else:
        return HttpResponseRedirect("/crawl/")

def script(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = db_scriptForm(request.session['user_id'], request.session['team'], request.POST, request.FILES)
            if form.is_valid():
                # form.save()
                new_batch = form.save()
                request.session['msg_data'] = 'create_supplier'
                request.session['supplier_name'] = request.POST['supplier_name']
                # user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                # start the task in the background
                # General Syntax -> schedule_batch.delay(teamName, batchName, inputFile, scriptName)
                # schedule_batch.delay(new_batch.id, new_batch.batch_name, new_batch.team, new_batch.input_file.name, new_batch.script_name, request.session['user_id'])
                return HttpResponseRedirect("/crawl/dashboard")
            else:
                for i in range(0,50):
                    print(i)
        else:
            form = db_scriptForm(request.session['user_id'], request.session['team'])
        return render(request, 'crawl/script.html', {
            'form': form
        })
    else:
        return HttpResponseRedirect("/crawl/")

def mybatches(request):
    if request.user.is_authenticated:
        db_batch_query_results = db_batch.objects.all().order_by('date')
        template = loader.get_template('crawl/mybatches.html')
        mod_data = []
        for data in db_batch_query_results:
            temp_data = {}
            if data.status == "completed":
                color_tag = "label label-success label-mini"
            elif data.status == "notstarted":
                color_tag = "label label-default label-mini"
            elif data.status == "paused":
                color_tag = "label label-warning label-mini"
            else:
                color_tag = "label label-warning label-mini"
            temp_data["batch_id"] = data.id
            temp_data["batch_name"] = data.batch_name
            temp_data["creation_date"] = data.creation_date
            temp_data["scheduled_date"] = data.scheduled_date
            temp_data["scheduled_time"] = data.scheduled_time
            temp_data["status"] = data.status
            temp_data["input_count"] = data.input_count
            temp_data["completion"] = data.completion
            temp_data["completion_found"] = data.completion_found
            temp_data["color_tag"] = color_tag
            mod_data.append(temp_data)
        context = {"db_batch_query_results": mod_data}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")

def batch(request, batch_id):
    if request.user.is_authenticated:
        current_batch = db_batch.objects.get(id=batch_id)
        template = loader.get_template('crawl/batch.html')
        context = {"batch_data": current_batch}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")

# def handler404(request):
#     return render(request, 'crawl/error_404.html', status=404)
# def handler500(request):
#     return render(request, 'crawl/error_500.html', status=500)