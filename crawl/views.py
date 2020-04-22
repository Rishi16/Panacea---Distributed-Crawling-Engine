import io
import shutil
from tailer import tail
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.http import HttpResponseRedirect
from django.template import loader
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from .models import User, db_batch, db_batch_run, db_script, db_script_archive, notifications, datasource_found, \
    datasource_tag_failed, datasource_proxy_blocked, datasource_pnf, datasource_other_exception
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render
from .tasks import schedule_batch, generate_batch_report, get_or_create_task_logger, server_usage
from crawl.forms import db_batchForm, db_scriptForm, db_edit_scriptForm, db_edit_batchForm, add_server
from crawl.Backbone.batch import Batch
import json
import os
import datetime

from django.http import JsonResponse


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
            last_five_notifications = notifications.objects.order_by('-id')[:5]
            # for single_notification in temp_notifications:
            #     last_five_notifications.append(single_notification.title)
            if 'msg_data' in request.session:
                if request.session['msg_data'] == 'welcome':
                    context = {
                        'username': request.session['username'],
                        'msg_to_show': 'Welcome to Panacea',
                        'detailed_message': 'Hover me to enable the Close Button. You can hide the left sidebar clicking on the button next to the logo.',
                        'notifications': last_five_notifications,
                    }
                    request.session['msg_data'] = ''
                elif request.session['msg_data'] == 'create_batch':
                    context = {
                        'username': request.session['username'],
                        'msg_to_show': request.session['batch_name'],
                        'detailed_message': 'Your batch has been created and scheduled properly. Please go to the search option to visit the batch.',
                        'notifications': last_five_notifications,
                    }
                    request.session['msg_data'] = ''
                elif request.session['msg_data'] == 'create_supplier':
                    context = {
                        'username': request.session['username'],
                        'msg_to_show': request.session['supplier_name'],
                        'detailed_message': 'Your supplier has been created/updated properly.',
                        'notifications': last_five_notifications,
                    }
                    request.session['msg_data'] = ''
                else:
                    request.session['username'] = request.user.username
                    context = {
                        'username': request.session['username'],
                        'msg_to_show': '',
                        'detailed_message': '',
                        'notifications': last_five_notifications,
                    }
                    request.session['msg_data'] = ''
                return HttpResponse(template.render(context, request))
            else:
                request.session['username'] = request.user.username
                context = {
                    'username': request.session['username'],
                    'msg_to_show': '',
                    'detailed_message': '',
                    'notifications': last_five_notifications,
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
            files = request.FILES.getlist('input_file')
            batch_name = request.POST['batch_name']
            # print(files)
            for count, _file in enumerate(files):
                # print(count, _file)
                request.FILES['input_file'] = _file
                request.POST = request.POST.copy()
                form = db_batchForm(request.session['user_id'], request.session['team'], request.POST, request.FILES)
                if len(files) > 1:
                    request.POST['batch_name'] = batch_name + '_' + str(count + 1)
                    # request.session['batch_name'] = request.session['batch_name'] + '_' + str(count+1)
                if form.is_valid():
                    # form.save()
                    new_batch = form.save()
                    request.session['msg_data'] = 'create_batch'
                    request.session['batch_name'] = request.POST['batch_name']
                    scheduled_time = request.POST['scheduled_time']
                    scheduled_time = datetime.datetime.strptime(scheduled_time, "%H:%M:%S")
                    print(scheduled_time)
                    hour_val = scheduled_time.strftime("%H")
                    minute_val = scheduled_time.strftime("%M")
                    # hour_val = "22"
                    # minute_val = "07"
                    print(hour_val, minute_val)
                    frequency = request.POST['frequency']
                    print(frequency)
                    frequency = frequency.split("|")

                    if len(frequency) > 1:
                        # weekly or monthly
                        if frequency[0] == "-3":
                            # Weekly
                            print("weekly")
                            week_numbers = frequency[1]
                            schedule, _ = CrontabSchedule.objects.get_or_create(minute=minute_val, hour=hour_val,
                                                                                day_of_week=week_numbers,
                                                                                day_of_month='*', month_of_year='*',
                                                                                timezone="Asia/Kolkata")
                            pt = PeriodicTask.objects.create(crontab=schedule,
                                                             name=new_batch.batch_name,
                                                             task='crawl.tasks.schedule_batch',
                                                             args=json.dumps([new_batch.id, new_batch.batch_name,
                                                                              new_batch.region, new_batch.team,
                                                                              new_batch.input_file.name,
                                                                              new_batch.script_name_id,
                                                                              request.session['user_id'],
                                                                              new_batch.scheduled_date,
                                                                              new_batch.scheduled_time], indent=4,
                                                                             sort_keys=True,
                                                                             default=str), )
                            new_batch.pt_id = pt.id
                            new_batch.save()
                            print(pt)
                            print(pt.id)

                        if frequency[0] == "-4":
                            # Monthly
                            print("monthly")
                            month_numbers = frequency[1]
                            schedule, _ = CrontabSchedule.objects.get_or_create(minute=minute_val, hour=hour_val,
                                                                                day_of_week='*',
                                                                                day_of_month=month_numbers,
                                                                                month_of_year='*', )
                            pt = PeriodicTask.objects.create(crontab=schedule,
                                                             name=new_batch.batch_name,
                                                             task='crawl.tasks.schedule_batch',
                                                             args=json.dumps([new_batch.id, new_batch.batch_name,
                                                                              new_batch.region, new_batch.team,
                                                                              new_batch.input_file.name,
                                                                              new_batch.script_name_id,
                                                                              request.session['user_id'],
                                                                              new_batch.scheduled_date,
                                                                              new_batch.scheduled_time], indent=4,
                                                                             sort_keys=True,
                                                                             default=str), )
                            new_batch.pt_id = pt.id
                            new_batch.save()
                            print(pt)
                            print(pt.id)
                    else:
                        # once or daily
                        if frequency[0] == "-1":
                            # Once
                            print("once")
                            schedule_batch.delay(new_batch.id, new_batch.batch_name, new_batch.region,
                                                 new_batch.team, new_batch.input_file.name, new_batch.script_name_id,
                                                 request.session['user_id'], new_batch.scheduled_date,
                                                 new_batch.scheduled_time)
                            new_batch.save()
                        elif frequency[0] == "-2":
                            # Daily
                            print("daily")
                            schedule, _ = CrontabSchedule.objects.get_or_create(minute=minute_val, hour=hour_val,
                                                                                day_of_week='*',
                                                                                day_of_month='*', month_of_year='*', )
                            pt = PeriodicTask.objects.create(crontab=schedule,
                                                             name=new_batch.batch_name,
                                                             task='crawl.tasks.schedule_batch',
                                                             args=json.dumps([new_batch.id, new_batch.batch_name,
                                                                              new_batch.region, new_batch.team,
                                                                              new_batch.input_file.name,
                                                                              new_batch.script_name_id,
                                                                              request.session['user_id'],
                                                                              new_batch.scheduled_date,
                                                                              new_batch.scheduled_time], indent=4,
                                                                             sort_keys=True,
                                                                             default=str), )
                            new_batch.pt_id = pt.id
                            new_batch.save()
                            print(pt)
                            print(pt.id)
                        else:
                            print("Unknown frequency for scheduler")
                    # user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                    # start the task in the background
                    # General Syntax -> schedule_batch.delay(teamName, batchName, inputFile, scriptName)

                    # schedule_batch.delay(new_batch.id, current_batch_run.id, new_batch.batch_name, new_batch.region,
                    #                      new_batch.team, new_batch.input_file.name, new_batch.script_name_id,
                    #                      request.session['user_id'], new_batch.scheduled_date, new_batch.scheduled_time)
                    # schedule, created = IntervalSchedule.objects.get_or_create(every = 50,
                    #                                                            period = IntervalSchedule.SECONDS)
                    # schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/2', hour='*', day_of_week='*',
                    #                                                     day_of_month='*', month_of_year='*', )
                    # pt = PeriodicTask.objects.create(crontab=schedule,
                    #                                  name=new_batch.batch_name, task='crawl.tasks.schedule_batch',
                    #                                  args=json.dumps([new_batch.id, new_batch.batch_name,
                    #                                                   new_batch.region, new_batch.team,
                    #                                                   new_batch.input_file.name, new_batch.script_name_id,
                    #                                                   request.session['user_id'], new_batch.scheduled_date,
                    #                                                   new_batch.scheduled_time], indent=4, sort_keys=True,
                    #                                                  default=str), )
                    # new_batch.pt_id = pt.id
                    # new_batch.save()
                    # print(pt)
                    # print(pt.id)
            return HttpResponseRedirect("/crawl/mybatches")
        else:
            form = db_batchForm(request.session['user_id'], request.session['team'])
        return render(request, 'crawl/new.html', {
            'form': form
        })
    else:
        return HttpResponseRedirect("/crawl/")


def edit_batch(request, batch_id):
    if request.user.is_authenticated:
        incident = get_object_or_404(db_batch, pk=batch_id)
        if request.method == 'POST':
            form = db_edit_batchForm(request.session['user_id'], request.session['team'], request.POST, request.FILES,
                                     instance=incident)
            if form.is_valid():
                # form.save()
                form.save()
                # current_batch_run = db_batch_run.objects.create(batch_id=batch_id)
                request.session['msg_data'] = 'create_batch'
                request.session['batch_name'] = request.POST['batch_name']
                # user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                # start the task in the background
                # General Syntax -> schedule_batch.delay(teamName, batchName, inputFile, scriptName)
                schedule_batch.delay(incident.id, incident.batch_name, incident.region,
                                     incident.team, incident.input_file.name, incident.script_name_id,
                                     request.session['user_id'], incident.scheduled_date, incident.scheduled_time)
                return HttpResponseRedirect("/crawl/mybatches")
            else:
                print('Invalid Form')
        else:
            form = db_edit_batchForm(request.session['user_id'], request.session['team'], instance=incident)
        return render(request, 'crawl/edit_batch.html', {
            'form': form
        })
    else:
        return HttpResponseRedirect("/crawl/")


def edit_script(request, script_id):
    if request.user.is_authenticated:
        incident = get_object_or_404(db_script, pk=script_id)
        if request.POST:
            form = db_edit_scriptForm(request.session['user_id'], request.session['team'], request.POST, request.FILES,
                                      instance=incident)
            if form.is_valid():
                form.save()
                request.session['msg_data'] = 'create_supplier'
                request.session['supplier_name'] = request.POST['supplier_name']
                return HttpResponseRedirect("/crawl/myscripts")
            else:
                return render(request, 'crawl/script.html', {'form': form})
        else:
            # form = db_scriptForm(instance=incident)
            form = db_edit_scriptForm(request.session['user_id'], request.session['team'], instance=incident)
        return render(request, 'crawl/edit_script.html', {'form': form})
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
                return HttpResponseRedirect("/crawl/myscripts")
            else:
                return render(request, "crawl/script.html", {'form': form})
        else:
            form = db_scriptForm(request.session['user_id'], request.session['team'])
        return render(request, 'crawl/script.html', {
            'form': form
        })
    else:
        return HttpResponseRedirect("/crawl/")


def mybatches(request):
    if request.user.is_authenticated:
        db_batch_query_results = db_batch.objects.filter(user_id=request.user.id).order_by('creation_date').reverse()
        template = loader.get_template('crawl/mybatches.html')
        mod_data = []
        for data in db_batch_query_results:
            temp_data = {}
            temp_data["batch_id"] = data.id
            temp_data["batch_name"] = data.batch_name
            temp_data["creation_date"] = data.creation_date
            temp_data["scheduled_date"] = data.scheduled_date
            temp_data["scheduled_time"] = data.scheduled_time

            batch_run = db_batch_run.objects.filter(batch_id=data.id).order_by('creation_date').reverse()
            if batch_run:
                batch_run = batch_run[0]
                temp_data["status"] = batch_run.status
                temp_data["input_count"] = batch_run.input_count
                temp_data["completion"] = batch_run.completion
                temp_data["completion_found"] = batch_run.completion_found
            else:
                temp_data["status"] = "notstarted"
                temp_data["input_count"] = ""
                temp_data["completion"] = ""
                temp_data["completion_found"] = ""
            try:
                if temp_data["status"] == "notstarted":
                    buttons = {'pause_button_onclick': 'restart_batch(' + str(data.id) + ')',
                               'pause_button_class': 'fa fa-refresh'}
                elif temp_data["status"] == "exception":
                    buttons = {'pause_button_onclick': 'restart_batch(' + str(data.id) + ')',
                               'pause_button_class': 'fa fa-refresh'}
                elif temp_data["status"] == "paused":
                    buttons = {'pause_button_onclick': 'resume_batch(' + str(data.id) + ')',
                               'pause_button_class': 'fa fa-play'}
                elif temp_data["status"] == "stopped":
                    buttons = {'pause_button_onclick': 'resume_batch(' + str(data.id) + ')',
                               'pause_button_class': 'fa fa-play'}
                elif temp_data["status"] == "running" or "initiating" in temp_data["status"]:
                    buttons = {'pause_button_onclick': 'pause_batch(' + str(data.id) + ')',
                               'pause_button_class': 'fa fa-pause'}
                elif temp_data["status"] == "completed":
                    buttons = {'pause_button_onclick': 'resume_batch(' + str(data.id) + ')',
                               'pause_button_class': 'fa fa-play'}
                else:
                    buttons = {'pause_button_onclick': 'restart_batch(' + str(data.id) + ')',
                               'pause_button_class': 'fa fa-refresh'}
                temp_data["buttons"] = buttons
            except:
                pass

            if temp_data["status"] in ["completed", "forced"]:
                color_tag = "label label-success label-mini"
            elif temp_data["status"] == "notstarted":
                color_tag = "label label-default label-mini"
            elif temp_data["status"] == "paused":
                color_tag = "label label-warning label-mini"
            elif temp_data["status"] == "exception":
                color_tag = "label label-danger label-mini"
            elif "initiating" in temp_data["status"]:
                color_tag = "label label-info label-mini"
            else:
                color_tag = "label label-primary label-mini"
            temp_data["color_tag"] = color_tag
            mod_data.append(temp_data)
        context = {"db_batch_query_results": mod_data}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")


def batch_proxy(request, batch_id):
    if request.user.is_authenticated:
        batch_name = db_batch.objects.get(id=batch_id).batch_name
        script_id = db_batch.objects.get(id=batch_id).script_name_id
        team_name = db_script.objects.get(id=script_id).team
        requests_log = 'e:\\Panacea\\team_data\\' + str(
            team_name) + '\\Batches\\' + str(batch_name) + '\\proxy_analysis.txt'
        with open(requests_log, 'r') as fr:
            proxy_data = fr.readlines(' + str(data.id) + ')

        template = loader.get_template('crawl/batch_proxy.html')
        mod_data = []
        for line in proxy_data:
            proxy_data = line.split('\t')
            temp_data = {}
            temp_data["proxy"] = proxy_data[0]
            temp_data["total"] = proxy_data[1]
            temp_data["success"] = proxy_data[2]
            temp_data["failed"] = proxy_data[3]
            temp_data["failurerate"] = proxy_data[4]

            batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
            if batch_run:
                batch_run = batch_run[0]
                temp_data["status"] = batch_run.status
                temp_data["input_count"] = batch_run.input_count
                temp_data["completion"] = batch_run.completion
                temp_data["completion_found"] = batch_run.completion_found
            else:
                temp_data["status"] = "notstarted"
                temp_data["input_count"] = ""
                temp_data["completion"] = ""
                temp_data["completion_found"] = ""

            if temp_data["status"] == "completed":
                color_tag = "label label-success label-mini"
            elif temp_data["status"] == "notstarted":
                color_tag = "label label-default label-mini"
            elif temp_data["status"] == "paused":
                color_tag = "label label-warning label-mini"
            else:
                color_tag = "label label-danger label-mini"
            temp_data["color_tag"] = color_tag
            mod_data.append(temp_data)
        context = {"db_batch_query_results": mod_data}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")


def servers(request, batch_id):
    if request.user.is_authenticated:
        try:
            current_batch = db_batch.objects.get(id=batch_id)
            batch_name = db_batch.objects.get(id=batch_id).batch_name
            batch_run_all = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
            if batch_run_all:
                batch_run = batch_run_all[0]
            if batch_run.report == False:
                report_button_disabled = 'disabled'
                report_button_href = ''
                generate_button_disabled = ''
            else:
                report_button_disabled = ''
                report_button_href = ' href=/crawl/download_report/' + str(current_batch.id)
                generate_button_disabled = 'disabled'

            if batch_run.status == "notstarted":
                buttons = {'edit_button_onclick': 'edit_batch()',
                           'edit_button_class': 'fa fa-pencil-square-o',
                           'edit_button_disabled': '',
                           'edit_button_text': ' Edit',
                           'pause_button_onclick': 'resume_batch()',
                           'pause_button_class': 'fa fa-play',
                           'pause_button_disabled': '',
                           'pause_button_text': ' Start',
                           'stop_button_onclick': 'stop_batch()',
                           'stop_button_class': 'fa fa-stop',
                           'stop_button_disabled': 'disabled',
                           'stop_button_text': ' Stop',
                           'delete_button_onclick': 'delete_batch()',
                           'delete_button_class': 'fa fa-trash-o',
                           'delete_button_disabled': '',
                           'delete_button_text': ' Delete',
                           'generate_button_onclick': 'generate_report()',
                           'generate_button_class': 'fa fa-file-excel-o',
                           'generate_button_disabled': generate_button_disabled,
                           'generate_button_text': ' Generate Report',
                           'generate_button_href': report_button_href,
                           'report_button_onclick': 'report_batch()',
                           'report_button_class': 'fa fa-file-excel-o',
                           'report_button_disabled': report_button_disabled,
                           'report_button_text': ' Report',
                           'report_button_href': report_button_href,
                           'recrawl_button_class': 'fa fa-repeat',
                           'recrawl_button_disabled': 'disabled',
                           'recrawl_button_text': ' Recrawl',
                           }
            elif batch_run.status == "paused":
                buttons = {'edit_button_onclick': 'edit_batch()',
                           'edit_button_class': 'fa fa-pencil-square-o',
                           'edit_button_disabled': '',
                           'edit_button_text': ' Edit',
                           'pause_button_onclick': 'resume_batch()',
                           'pause_button_class': 'fa fa-play',
                           'pause_button_disabled': '',
                           'pause_button_text': ' Resume',
                           'stop_button_onclick': 'stop_batch()',
                           'stop_button_class': 'fa fa-stop',
                           'stop_button_disabled': '',
                           'stop_button_text': ' Stop',
                           'delete_button_onclick': 'delete_batch()',
                           'delete_button_class': 'fa fa-trash-o',
                           'delete_button_disabled': '',
                           'delete_button_text': ' Delete',
                           'generate_button_onclick': 'generate_report()',
                           'generate_button_class': 'fa fa-file-excel-o',
                           'generate_button_disabled': generate_button_disabled,
                           'generate_button_text': ' Generate Report',
                           'generate_button_href': report_button_href,
                           'report_button_onclick': 'report_batch()',
                           'report_button_class': 'fa fa-file-excel-o',
                           'report_button_disabled': report_button_disabled,
                           'report_button_text': ' Report',
                           'report_button_href': report_button_href,
                           'recrawl_button_class': 'fa fa-file-excel-o',
                           'recrawl_button_disabled': '',
                           'recrawl_button_text': ' Recrawl',
                           }
            elif batch_run.status == "stopped":
                buttons = {'edit_button_onclick': 'edit_batch()',
                           'edit_button_class': 'fa fa-pencil-square-o',
                           'edit_button_disabled': '',
                           'edit_button_text': ' Edit',
                           'pause_button_onclick': 'resume_batch()',
                           'pause_button_class': 'fa fa-play',
                           'pause_button_disabled': '',
                           'pause_button_text': ' Resume',
                           'stop_button_onclick': 'stop_batch()',
                           'stop_button_class': 'fa fa-stop',
                           'stop_button_disabled': 'disabled',
                           'stop_button_text': ' Stop',
                           'delete_button_onclick': 'delete_batch()',
                           'delete_button_class': 'fa fa-trash-o',
                           'delete_button_disabled': '',
                           'delete_button_text': ' Delete',
                           'generate_button_onclick': 'generate_report()',
                           'generate_button_class': 'fa fa-file-excel-o',
                           'generate_button_disabled': generate_button_disabled,
                           'generate_button_text': ' Generate Report',
                           'generate_button_href': report_button_href,
                           'report_button_onclick': 'report_batch()',
                           'report_button_class': 'fa fa-file-excel-o',
                           'report_button_disabled': report_button_disabled,
                           'report_button_text': ' Report',
                           'report_button_href': report_button_href,
                           'recrawl_button_class': 'fa fa-file-excel-o',
                           'recrawl_button_disabled': '',
                           'recrawl_button_text': ' Recrawl',
                           }
            elif batch_run.status == "running":
                buttons = {'edit_button_onclick': 'edit_batch()',
                           'edit_button_class': 'fa fa-pencil-square-o',
                           'edit_button_disabled': '',
                           'edit_button_text': ' Edit',
                           'pause_button_onclick': 'pause_batch()',
                           'pause_button_class': 'fa fa-play',
                           'pause_button_disabled': '',
                           'pause_button_text': ' Pause',
                           'stop_button_onclick': 'stop_batch()',
                           'stop_button_class': 'fa fa-stop',
                           'stop_button_disabled': '',
                           'stop_button_text': ' Stop',
                           'delete_button_onclick': 'delete_batch()',
                           'delete_button_class': 'fa fa-trash-o',
                           'delete_button_disabled': '',
                           'delete_button_text': ' Delete',
                           'generate_button_onclick': 'generate_report()',
                           'generate_button_class': 'fa fa-file-excel-o',
                           'generate_button_disabled': generate_button_disabled,
                           'generate_button_text': ' Generate Report',
                           'generate_button_href': report_button_href,
                           'report_button_onclick': 'report_batch()',
                           'report_button_class': 'fa fa-file-excel-o',
                           'report_button_disabled': report_button_disabled,
                           'report_button_text': ' Report',
                           'report_button_href': report_button_href,
                           'recrawl_button_class': 'fa fa-file-excel-o',
                           'recrawl_button_disabled': 'disabled',
                           'recrawl_button_text': ' Recrawl',
                           }
            elif batch_run.status == "completed":
                buttons = {'edit_button_onclick': 'edit_batch()',
                           'edit_button_class': 'fa fa-pencil-square-o',
                           'edit_button_disabled': '',
                           'edit_button_text': ' Edit',
                           'pause_button_onclick': 'resume_batch()',
                           'pause_button_class': 'fa fa-play',
                           'pause_button_disabled': '',
                           'pause_button_text': ' Restart',
                           'stop_button_onclick': 'stop_batch()',
                           'stop_button_class': 'fa fa-stop',
                           'stop_button_disabled': 'disabled',
                           'stop_button_text': ' Stop',
                           'delete_button_onclick': 'delete_batch()',
                           'delete_button_class': 'fa fa-trash-o',
                           'delete_button_disabled': '',
                           'delete_button_text': ' Delete',
                           'generate_button_onclick': 'generate_report()',
                           'generate_button_class': 'fa fa-file-excel-o',
                           'generate_button_disabled': generate_button_disabled,
                           'generate_button_text': ' Generate Report',
                           'generate_button_href': report_button_href,
                           'report_button_onclick': 'report_batch()',
                           'report_button_class': 'fa fa-file-excel-o',
                           'report_button_disabled': report_button_disabled,
                           'report_button_text': ' Report',
                           'report_button_href': report_button_href,
                           'recrawl_button_class': 'fa fa-file-excel-o',
                           'recrawl_button_disabled': '',
                           'recrawl_button_text': ' Recrawl',
                           }
            else:
                buttons = {'edit_button_onclick': 'edit_batch()',
                           'edit_button_class': 'fa fa-pencil-square-o',
                           'edit_button_disabled': '',
                           'edit_button_text': ' Edit',
                           'pause_button_onclick': 'resume_batch()',
                           'pause_button_class': 'fa fa-play',
                           'pause_button_disabled': '',
                           'pause_button_text': ' Restart',
                           'stop_button_onclick': 'stop_batch()',
                           'stop_button_class': 'fa fa-stop',
                           'stop_button_disabled': 'disabled',
                           'stop_button_text': ' Stop',
                           'delete_button_onclick': 'delete_batch()',
                           'delete_button_class': 'fa fa-trash-o',
                           'delete_button_disabled': '',
                           'delete_button_text': ' Delete',
                           'generate_button_onclick': 'generate_report()',
                           'generate_button_class': 'fa fa-file-excel-o',
                           'generate_button_disabled': generate_button_disabled,
                           'generate_button_text': ' Generate Report',
                           'generate_button_href': report_button_href,
                           'report_button_onclick': 'report_batch()',
                           'report_button_class': 'fa fa-file-excel-o',
                           'report_button_disabled': report_button_disabled,
                           'report_button_text': ' Report',
                           'report_button_href': report_button_href,
                           'recrawl_button_class': 'fa fa-file-excel-o',
                           'recrawl_button_disabled': '',
                           'recrawl_button_text': ' Recrawl',
                           }
            reports = []
            for i in batch_run_all:
                reports.append({'report': i.id, 'creation_date': i.creation_date.ctime()})
            script_id = db_batch.objects.get(id=batch_id).script_name_id
            team_name = db_script.objects.get(id=script_id).team
            server_details = db_script.objects.get(id=script_id).servers
            server_list = server_usage(server_details)

            template = loader.get_template('crawl/servers.html')

            context = {"server_list": server_list, 'batch_data': {'batch_name': batch_name}, "buttons": buttons,
                       "reports": reports}
            return HttpResponse(template.render(context, request))
        except Exception as e:
            print(e)
    else:
        return HttpResponseRedirect("/crawl/")


def batch_logs(request, batch_id):
    if request.user.is_authenticated:
        batch_name = db_batch.objects.get(id=batch_id).batch_name
        script_id = db_batch.objects.get(id=batch_id).script_name_id
        team_name = db_script.objects.get(id=script_id).team
        batch_log = 'e:\\Panacea\\team_data\\' + str(
            team_name) + '\\Batches\\' + str(batch_name) + '\\logs\\batch.log'
        my_file = open(batch_log, 'r')
        response = HttpResponse(my_file.read(), content_type='text/plain')
        response['Content-Disposition'] = 'inline;filename=batch.log'
        return response
    else:
        return HttpResponseRedirect("/crawl/")


def mybatchestop(request):
    if request.user.is_authenticated:
        db_batch_query_results = db_batch.objects.filter(user_id=request.user.id).order_by('creation_date').reverse()
        template = loader.get_template('crawl/mybatchestop.html')
        mod_data = []
        for data in db_batch_query_results:
            temp_data = {}
            temp_data["batch_id"] = data.id
            temp_data["batch_name"] = data.batch_name
            temp_data["creation_date"] = data.creation_date
            temp_data["scheduled_date"] = data.scheduled_date
            temp_data["scheduled_time"] = data.scheduled_time

            batch_run = db_batch_run.objects.filter(batch_id=data.id).order_by('creation_date').reverse()
            if batch_run:
                batch_run = batch_run[0]
                temp_data["status"] = batch_run.status
                temp_data["input_count"] = batch_run.input_count
                temp_data["completion"] = batch_run.completion
                temp_data["completion_found"] = batch_run.completion_found
            else:
                temp_data["status"] = "notstarted"
                temp_data["input_count"] = ""
                temp_data["completion"] = ""
                temp_data["completion_found"] = ""

            if temp_data["status"] == "completed":
                color_tag = "label label-success label-mini"
            elif temp_data["status"] == "notstarted":
                color_tag = "label label-default label-mini"
            elif temp_data["status"] == "paused":
                color_tag = "label label-warning label-mini"
            elif temp_data["status"] == "exception":
                color_tag = "label label-danger label-mini"
            elif "initiating" in temp_data["status"]:
                color_tag = "label label-info label-mini"
            else:
                color_tag = "label label-danger label-mini"
            temp_data["color_tag"] = color_tag
            mod_data.append(temp_data)
        context = {"db_batch_query_results": mod_data}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")


def update_mybatches_status(request):
    if request.user.is_authenticated:
        db_batch_query_results = db_batch.objects.filter(user_id=request.user.id).order_by('creation_date').reverse()
        mod_data = []
        for data in db_batch_query_results:
            temp_data = {}
            temp_data["batch_id"] = data.id
            temp_data["batch_name"] = data.batch_name
            temp_data["creation_date"] = data.creation_date
            temp_data["scheduled_date"] = data.scheduled_date
            temp_data["scheduled_time"] = data.scheduled_time

            batch_run = db_batch_run.objects.filter(batch_id=data.id).order_by('creation_date').reverse()
            if batch_run:
                batch_run = batch_run[0]
                temp_data["status"] = batch_run.status
                temp_data["input_count"] = batch_run.input_count
                temp_data["completion"] = batch_run.completion
                temp_data["completion_found"] = batch_run.completion_found
            else:
                temp_data["status"] = "notstarted"
                temp_data["input_count"] = ""
                temp_data["completion"] = ""
                temp_data["completion_found"] = ""

            if temp_data["status"] == "notstarted":
                buttons = {'pause_button_onclick': 'restart_batch(' + str(data.id) + ')',
                           'pause_button_class': 'fa fa-refresh'}
            elif temp_data["status"] == "exception":
                buttons = {'pause_button_onclick': 'restart_batch(' + str(data.id) + ')',
                           'pause_button_class': 'fa fa-refresh'}
            elif batch_run.status == "paused":
                buttons = {'pause_button_onclick': 'resume_batch(' + str(data.id) + ')',
                           'pause_button_class': 'fa fa-play'}
            elif batch_run.status == "stopped":
                buttons = {'pause_button_onclick': 'resume_batch(' + str(data.id) + ')',
                           'pause_button_class': 'fa fa-play'}
            elif batch_run.status == "running" or "initiating" in batch_run.status:
                buttons = {'pause_button_onclick': 'pause_batch(' + str(data.id) + ')',
                           'pause_button_class': 'fa fa-pause'}
            elif batch_run.status == "completed":
                buttons = {'pause_button_onclick': 'resume_batch(' + str(data.id) + ')',
                           'pause_button_class': 'fa fa-play'}
            else:
                buttons = {'pause_button_onclick': 'resume_batch(' + str(data.id) + ')',
                           'pause_button_class': 'fa fa-play'}
            temp_data["buttons"] = buttons

            if temp_data["status"] in ["completed", "forced"]:
                color_tag = "label label-success label-mini"
            elif temp_data["status"] == "notstarted":
                color_tag = "label label-default label-mini"
            elif temp_data["status"] == "paused":
                color_tag = "label label-warning label-mini"
            elif temp_data["status"] == "exception":
                color_tag = "label label-danger label-mini"
            elif "initiating" in temp_data["status"]:
                color_tag = "label label-info label-mini"
            else:
                color_tag = "label label-primary label-mini"
            temp_data["color_tag"] = color_tag
            mod_data.append(temp_data)
        return JsonResponse({'data': mod_data})
    else:
        return HttpResponseRedirect("/crawl/")


def batch(request, batch_id):
    if request.user.is_authenticated:
        current_batch = db_batch.objects.get(id=batch_id)
        batch_run_all = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
        if batch_run_all:
            batch_run = batch_run_all[0]
        template = loader.get_template('crawl/batch.html')

        # batch_status = {}
        # batch_status['status'] = str(batch_run.status)
        # batch_status['completion'] = str(int((int(batch_run.completion) / int(batch_run.input_count)) * 100))
        # batch_status['completion_found'] = str(int((int(batch_run.completion_found) / int(batch_run.input_count)) * 100))
        # batch_status['completion_pnf'] = str(int((int(batch_run.completion_pnf) / int(batch_run.input_count)) * 100))
        # batch_status['completion_proxy_blocked'] = str(int((int(batch_run.completion_proxy_blocked) / int(batch_run.input_count)) * 100))
        # batch_status['completion_tag_failed'] = str(int((int(batch_run.completion_tag_failed) / int(batch_run.input_count)) * 100))
        batch_status = {
            'status': batch_run.status,
            'completion': batch_run.completion,
            'completion_pcnt': str(int((int(batch_run.completion) / int(batch_run.input_count)) * 100)),
            'completion_found': batch_run.completion_found,
            'completion_found_pcnt': str(int((int(batch_run.completion_found) / int(batch_run.input_count)) * 100)),
            'completion_pnf': batch_run.completion_pnf,
            'completion_pnf_pcnt': str(int((int(batch_run.completion_pnf) / int(batch_run.input_count)) * 100)),
            'completion_proxy_blocked': batch_run.completion_proxy_blocked,
            'completion_proxy_blocked_pcnt': str(
                int((int(batch_run.completion_proxy_blocked) / int(batch_run.input_count)) * 100)),
            'completion_tag_failed': batch_run.completion_tag_failed,
            'completion_tag_failed_pcnt': str(
                int((int(batch_run.completion_tag_failed) / int(batch_run.input_count)) * 100)),

        }

        if batch_run.report == False:
            report_button_disabled = 'disabled'
            report_button_href = ''
            generate_button_disabled = ''
        else:
            report_button_disabled = ''
            report_button_href = ' href=/crawl/download_report/' + str(current_batch.id)
            generate_button_disabled = 'disabled'

        if batch_run.status == "notstarted":
            buttons = {'edit_button_onclick': 'edit_batch()',
                       'edit_button_class': 'fa fa-pencil-square-o',
                       'edit_button_disabled': '',
                       'edit_button_text': ' Edit',
                       'pause_button_onclick': 'restart_batch()',
                       'pause_button_class': 'fa fa-refresh',
                       'pause_button_disabled': '',
                       'pause_button_text': ' Start',
                       'stop_button_onclick': 'stop_batch()',
                       'stop_button_class': 'fa fa-stop',
                       'stop_button_disabled': 'disabled',
                       'stop_button_text': ' Stop',
                       'delete_button_onclick': 'delete_batch()',
                       'delete_button_class': 'fa fa-trash-o',
                       'delete_button_disabled': '',
                       'delete_button_text': ' Delete',
                       'generate_button_onclick': 'generate_report()',
                       'generate_button_class': 'fa fa-file-excel-o',
                       'generate_button_disabled': generate_button_disabled,
                       'generate_button_text': ' Generate Report',
                       'generate_button_href': report_button_href,
                       'report_button_onclick': 'report_batch()',
                       'report_button_class': 'fa fa-file-excel-o',
                       'report_button_disabled': report_button_disabled,
                       'report_button_text': ' Report',
                       'report_button_href': report_button_href,
                       'recrawl_button_class': 'fa fa-repeat',
                       'recrawl_button_disabled': 'disabled',
                       'recrawl_button_text': ' Recrawl',
                       }
        elif batch_run.status == "paused":
            buttons = {'edit_button_onclick': 'edit_batch()',
                       'edit_button_class': 'fa fa-pencil-square-o',
                       'edit_button_disabled': '',
                       'edit_button_text': ' Edit',
                       'pause_button_onclick': 'resume_batch()',
                       'pause_button_class': 'fa fa-play',
                       'pause_button_disabled': '',
                       'pause_button_text': ' Resume',
                       'stop_button_onclick': 'stop_batch()',
                       'stop_button_class': 'fa fa-stop',
                       'stop_button_disabled': '',
                       'stop_button_text': ' Stop',
                       'delete_button_onclick': 'delete_batch()',
                       'delete_button_class': 'fa fa-trash-o',
                       'delete_button_disabled': '',
                       'delete_button_text': ' Delete',
                       'generate_button_onclick': 'generate_report()',
                       'generate_button_class': 'fa fa-file-excel-o',
                       'generate_button_disabled': generate_button_disabled,
                       'generate_button_text': ' Generate Report',
                       'generate_button_href': report_button_href,
                       'report_button_onclick': 'report_batch()',
                       'report_button_class': 'fa fa-file-excel-o',
                       'report_button_disabled': report_button_disabled,
                       'report_button_text': ' Report',
                       'report_button_href': report_button_href,
                       'recrawl_button_class': 'fa fa-file-excel-o',
                       'recrawl_button_disabled': '',
                       'recrawl_button_text': ' Recrawl',
                       }
        elif batch_run.status == "stopped":
            buttons = {'edit_button_onclick': 'edit_batch()',
                       'edit_button_class': 'fa fa-pencil-square-o',
                       'edit_button_disabled': '',
                       'edit_button_text': ' Edit',
                       'pause_button_onclick': 'resume_batch()',
                       'pause_button_class': 'fa fa-play',
                       'pause_button_disabled': '',
                       'pause_button_text': ' Resume',
                       'stop_button_onclick': 'stop_batch()',
                       'stop_button_class': 'fa fa-stop',
                       'stop_button_disabled': 'disabled',
                       'stop_button_text': ' Stop',
                       'delete_button_onclick': 'delete_batch()',
                       'delete_button_class': 'fa fa-trash-o',
                       'delete_button_disabled': '',
                       'delete_button_text': ' Delete',
                       'generate_button_onclick': 'generate_report()',
                       'generate_button_class': 'fa fa-file-excel-o',
                       'generate_button_disabled': generate_button_disabled,
                       'generate_button_text': ' Generate Report',
                       'generate_button_href': report_button_href,
                       'report_button_onclick': 'report_batch()',
                       'report_button_class': 'fa fa-file-excel-o',
                       'report_button_disabled': report_button_disabled,
                       'report_button_text': ' Report',
                       'report_button_href': report_button_href,
                       'recrawl_button_class': 'fa fa-file-excel-o',
                       'recrawl_button_disabled': '',
                       'recrawl_button_text': ' Recrawl',
                       }
        elif batch_run.status == "running" or 'initiating' in batch_run.status:
            buttons = {'edit_button_onclick': 'edit_batch()',
                       'edit_button_class': 'fa fa-pencil-square-o',
                       'edit_button_disabled': '',
                       'edit_button_text': ' Edit',
                       'pause_button_onclick': 'pause_batch()',
                       'pause_button_class': 'fa fa-play',
                       'pause_button_disabled': '',
                       'pause_button_text': ' Pause',
                       'stop_button_onclick': 'stop_batch()',
                       'stop_button_class': 'fa fa-stop',
                       'stop_button_disabled': '',
                       'stop_button_text': ' Stop',
                       'delete_button_onclick': 'delete_batch()',
                       'delete_button_class': 'fa fa-trash-o',
                       'delete_button_disabled': '',
                       'delete_button_text': ' Delete',
                       'generate_button_onclick': 'generate_report()',
                       'generate_button_class': 'fa fa-file-excel-o',
                       'generate_button_disabled': generate_button_disabled,
                       'generate_button_text': ' Generate Report',
                       'generate_button_href': report_button_href,
                       'report_button_onclick': 'report_batch()',
                       'report_button_class': 'fa fa-file-excel-o',
                       'report_button_disabled': report_button_disabled,
                       'report_button_text': ' Report',
                       'report_button_href': report_button_href,
                       'recrawl_button_class': 'fa fa-file-excel-o',
                       'recrawl_button_disabled': 'disabled',
                       'recrawl_button_text': ' Recrawl',
                       }
        elif batch_run.status == "completed":
            buttons = {'edit_button_onclick': 'edit_batch()',
                       'edit_button_class': 'fa fa-pencil-square-o',
                       'edit_button_disabled': '',
                       'edit_button_text': ' Edit',
                       'pause_button_onclick': 'restart_batch()',
                       'pause_button_class': 'fa fa-refresh',
                       'pause_button_disabled': '',
                       'pause_button_text': ' Restart',
                       'stop_button_onclick': 'stop_batch()',
                       'stop_button_class': 'fa fa-stop',
                       'stop_button_disabled': 'disabled',
                       'stop_button_text': ' Stop',
                       'delete_button_onclick': 'delete_batch()',
                       'delete_button_class': 'fa fa-trash-o',
                       'delete_button_disabled': '',
                       'delete_button_text': ' Delete',
                       'generate_button_onclick': 'generate_report()',
                       'generate_button_class': 'fa fa-file-excel-o',
                       'generate_button_disabled': generate_button_disabled,
                       'generate_button_text': ' Generate Report',
                       'generate_button_href': report_button_href,
                       'report_button_onclick': 'report_batch()',
                       'report_button_class': 'fa fa-file-excel-o',
                       'report_button_disabled': report_button_disabled,
                       'report_button_text': ' Report',
                       'report_button_href': report_button_href,
                       'recrawl_button_class': 'fa fa-file-excel-o',
                       'recrawl_button_disabled': '',
                       'recrawl_button_text': ' Recrawl',
                       }
        else:
            buttons = {'edit_button_onclick': 'edit_batch()',
                       'edit_button_class': 'fa fa-pencil-square-o',
                       'edit_button_disabled': '',
                       'edit_button_text': ' Edit',
                       'pause_button_onclick': 'resume_batch()',
                       'pause_button_class': 'fa fa-play',
                       'pause_button_disabled': '',
                       'pause_button_text': ' Restart',
                       'stop_button_onclick': 'stop_batch()',
                       'stop_button_class': 'fa fa-stop',
                       'stop_button_disabled': 'disabled',
                       'stop_button_text': ' Stop',
                       'delete_button_onclick': 'delete_batch()',
                       'delete_button_class': 'fa fa-trash-o',
                       'delete_button_disabled': '',
                       'delete_button_text': ' Delete',
                       'generate_button_onclick': 'generate_report()',
                       'generate_button_class': 'fa fa-file-excel-o',
                       'generate_button_disabled': generate_button_disabled,
                       'generate_button_text': ' Generate Report',
                       'generate_button_href': report_button_href,
                       'report_button_onclick': 'report_batch()',
                       'report_button_class': 'fa fa-file-excel-o',
                       'report_button_disabled': report_button_disabled,
                       'report_button_text': ' Report',
                       'report_button_href': report_button_href,
                       'recrawl_button_class': 'fa fa-file-excel-o',
                       'recrawl_button_disabled': '',
                       'recrawl_button_text': ' Recrawl',
                       }
        reports = []
        for i in batch_run_all:
            reports.append({'report': i.id, 'creation_date': i.creation_date.ctime()})
        context = {"batch_data": current_batch, "batch_status": batch_status, "buttons": buttons, "reports": reports}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")


def update_batch_status(request, batch_id):
    if request.user.is_authenticated:
        current_batch = db_batch.objects.get(id=batch_id)
        batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
        if batch_run:
            batch_run = batch_run[0]
        # server_speed = batch_run.server_speed.split("|")
        # server_speed = [int(x) for x in server_speed]
        data = {
            'id': current_batch.id,
            'batch_name': current_batch.batch_name,
            'input': batch_run.input_count,
            'status': batch_run.status,
            'completion': batch_run.completion,
            'completion_pcnt': str(int((int(batch_run.completion) / int(batch_run.input_count)) * 100)),
            'completion_found': batch_run.completion_found,
            'completion_found_pcnt': str(int((int(batch_run.completion_found) / int(batch_run.input_count)) * 100)),
            'completion_pnf': batch_run.completion_pnf,
            'completion_pnf_pcnt': str(int((int(batch_run.completion_pnf) / int(batch_run.input_count)) * 100)),
            'completion_proxy_blocked': batch_run.completion_proxy_blocked,
            'completion_proxy_blocked_pcnt': str(
                int((int(batch_run.completion_proxy_blocked) / int(batch_run.input_count)) * 100)),
            'completion_tag_failed': batch_run.completion_tag_failed,
            'completion_tag_failed_pcnt': str(
                int((int(batch_run.completion_tag_failed) / int(batch_run.input_count)) * 100)),
            # 'server_speed': server_speed,

        }
        # return HttpResponse(json.dumps(data))
        return JsonResponse({'data': data})
    else:
        return HttpResponseRedirect("/crawl/")


def change_batch_status(request, batch_id, status):
    if request.user.is_authenticated:
        current_batch = db_batch.objects.get(id=batch_id)
        batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
        if batch_run:
            batch_run = batch_run[0]
        batch_run.status = status
        batch_run.save()
        if status in ["resumed", "restarted"]:
            db_batch_run_instance = db_batch_run.objects.create(batch_id=batch_id)
            db_batch_run_instance.input_count = batch_run.input_count
            db_batch_run_instance.completion = batch_run.completion
            db_batch_run_instance.completion_found = batch_run.completion_found
            db_batch_run_instance.completion_pnf = batch_run.completion_pnf
            db_batch_run_instance.completion_proxy_blocked = batch_run.completion_proxy_blocked
            db_batch_run_instance.completion_tag_failed = batch_run.completion_tag_failed
            db_batch_run_instance.completion_other = batch_run.completion_other
            db_batch_run_instance.status = status
            db_batch_run_instance.save()
            schedule_batch.delay(current_batch.id, current_batch.batch_name,
                                 current_batch.region, current_batch.team, current_batch.input_file.name,
                                 current_batch.script_name_id, request.session['user_id'], current_batch.scheduled_date,
                                 current_batch.scheduled_time, resume=True)
        else:
            if status == 'paused':
                script_id = db_batch.objects.get(id=batch_id).script_name_id
                team_name = db_script.objects.get(id=script_id).team
                batch_name = db_batch.objects.get(id=batch_id).batch_name
                server_details = db_script.objects.get(id=script_id).servers
                server_details = server_details.split('|')
                server_details = [[temp.split(':')[0], temp.split(':')[1], temp.split(':')[2]] for temp in
                                  server_details]
                for server in server_details:
                    try:
                        server_con_details = server
                        server_name = server_con_details[0]
                        server_ip = server_con_details[1]
                        remote_path = '\\\\{}\\e$\\panacea\\Team_data'.format(server_ip)
                        remote_batch_path = os.path.join(remote_path, str(team_name), str(batch_name))
                        print('stopping thread process on server')
                        with open(os.path.join(remote_batch_path, 'properties.pbf'), 'r+') as fr:
                            data = fr.readlines()
                            for i, line in enumerate(data):
                                if line.split('=')[0] == 'stop':
                                    data[i] = 'stop=1'
                        with open(os.path.join(remote_batch_path, 'properties.pbf'), 'w') as fr:
                            fr.write(''.join([i for i in data]))
                    except Exception as e:
                        print(str(server_name), str(e))
        # return HttpResponse(json.dumps(data))
        return JsonResponse({'data': 'success'})
    else:
        return HttpResponseRedirect("/crawl/")


def generate_report(request, batch_id):
    if request.user.is_authenticated:
        current_batch = db_batch.objects.get(id=batch_id)
        batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
        if batch_run:
            batch_run = batch_run[0]
        report_generation_val = generate_batch_report(batch_run.server_report, current_batch.team,
                                                      current_batch.batch_name, batch_id, batch_run.id)
        report_button_href = '/crawl/download_report/' + str(current_batch.id)
        return JsonResponse({'msg': report_generation_val, 'report_location': report_button_href})
        # generate_batch_report2.delay(current_batch.id, current_batch.batch_name, current_batch.team,
        #                       batch_run.server_report)
    else:
        return HttpResponseRedirect("/crawl/")


def generate_run_report(request, batch_id, batch_run_id):
    if request.user.is_authenticated:
        current_batch = db_batch.objects.get(id=batch_id)
        batch_run = db_batch_run.objects.filter(id=batch_run_id)
        if batch_run:
            batch_run = batch_run[0]
        report_generation_val = generate_batch_report(batch_run.server_report, current_batch.team,
                                                      current_batch.batch_name, batch_id, batch_run.id)
        report_button_href = '/crawl/download_report/' + str(current_batch.id)
        return JsonResponse({'msg': report_generation_val, 'report_location': report_button_href})
        # generate_batch_report2.delay(current_batch.id, current_batch.batch_name, current_batch.team,
        #                       batch_run.server_report)
    else:
        return HttpResponseRedirect("/crawl/")


# def download_report1(request, batch_id):
#     if request.user.is_authenticated:
#         current_batch = db_batch.objects.get(id=batch_id)
#         batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
#         if batch_run:
#             batch_run = batch_run[0]
#         report_value = batch_run.report
#         if os.path.exists(report_value == True):
#
#             with open(file_path, 'rb') as fh:
#                 response = HttpResponse(fh.read(), content_type="text/plain")
#                 response['Content-Disposition'] = 'attachment; filename="' + os.path.basename(file_path)
#                 return response
#     else:
#         return HttpResponseRedirect("/crawl/")

def download_report(request, batch_id):
    if request.user.is_authenticated:
        batch_run_id = request.GET.get('run_id', '')
        if batch_run_id:
            batch_run = db_batch_run.objects.filter(id=batch_run_id)
            if batch_run:
                batch_run = batch_run[0]
        else:
            batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
            if batch_run:
                batch_run = batch_run[0]
        current_batch = db_batch.objects.get(id=batch_id)
        report_value = batch_run.report
        batch_name = current_batch.batch_name
        if report_value:
            output_file_path = batch_run.report_location
            output_file_path = os.path.join(output_file_path, batch_name)
            print("Downloading file - ", output_file_path + ".zip")
            # return JsonResponse({'success': True})
            # Files (local path) to put in the .zip
            # FIXME: Change this (get paths from DB etc)
            # filenames = [os.path.join(output_file_path, "final_data.txt"),
            #              os.path.join(output_file_path, "pnf.txt"),
            #              os.path.join(output_file_path, "tag_failed.txt"),
            #              os.path.join(output_file_path, "proxy_blocked.txt"),
            #              os.path.join(output_file_path, "other_exception.txt")]
            #
            # # Folder name in ZIP archive which contains the above files
            # # E.g [thearchive.zip]/somefiles/file2.txt
            # zip_subdir = "output_files"
            # zip_filename = "%s.zip" % zip_subdir
            #
            # # Open StringIO to grab in-memory ZIP contents
            # s = BytesIO()
            #
            # # The zip compressor
            # zf = zipfile.ZipFile(s, "w")
            #
            # for fpath in filenames:
            #     # Calculate path for file in zip
            #     fdir, fname = os.path.split(fpath)
            #     zip_path = os.path.join(zip_subdir, fname)
            #     print(zip_path)
            #     print(fpath)
            #
            #     # Add file, at correct path
            #     zf.write(fpath, zip_path)
            #
            # # Must close zip for all contents to be written
            # zf.close()

            # Grab ZIP file from in-memory, make response with correct MIME-type
            # resp = HttpResponse(output_file_path, content_type = "application/x-zip-compressed")
            # resp['Content-Disposition'] = 'attachment; filename=%s' % batch_name
            # return resp
            # with open(output_file_path + ".zip", 'r') as zf:
            response = HttpResponse(io.open(output_file_path + ".zip", mode="rb").read(),
                                    content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename="' + batch_name + ".zip"
            return response
        else:
            return JsonResponse({'msg': 'Report not generated/found for ' + str(batch_run_id)})
    else:
        return HttpResponseRedirect("/crawl/")


# def handler404(request):
#     return render(request, 'crawl/error_404.html', status=404)
# def handler500(request):
#     return render(request, 'crawl/error_500.html', status=500)

def delete_batch(request, batch_id):
    if request.user.is_authenticated:
        batch_name = db_batch.objects.get(id=batch_id).batch_name
        script_id = db_batch.objects.get(id=batch_id).script_name_id
        team_name = db_script.objects.get(id=script_id).team
        server_details = db_script.objects.get(id=script_id).servers
        server_details = server_details.split('|')
        server_details = [[temp.split(':')[0], temp.split(':')[1], temp.split(':')[2]] for temp in server_details]

        for each_server in server_details:
            try:
                print('Deleting: ', batch_name, script_id, team_name, each_server[0])
                server_name = each_server[1]
                server_folder = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
                    team_name) + '\\' + str(batch_name)
                print(server_folder)
                if os.path.exists(server_folder):
                    print('final delete')
                    shutil.rmtree(server_folder)
            except Exception as e:
                print('Unable to delete:', batch_name, each_server[0])

        batch_run = db_batch_run.objects.filter(batch_id=batch_id)
        for temp_batch_run in batch_run:
            batch_run_id = temp_batch_run.id
            datasource_found.objects.filter(batch_run_id=batch_run_id).delete()
            datasource_tag_failed.objects.filter(batch_run_id=batch_run_id).delete()
            datasource_proxy_blocked.objects.filter(batch_run_id=batch_run_id).delete()
            datasource_pnf.objects.filter(batch_run_id=batch_run_id).delete()
            datasource_other_exception.objects.filter(batch_run_id=batch_run_id).delete()
        pt_id = db_batch.objects.get(id=batch_id).pt_id
        if pt_id != "":
            print("===========", pt_id)
            pt = PeriodicTask.objects.get(id=pt_id)
            pt.delete()
        db_batch_run.objects.filter(batch_id=batch_id).delete()
        db_batch.objects.filter(id=batch_id).delete()
        return JsonResponse({'data': 'success'})
    else:
        return HttpResponseRedirect("/crawl/mybatches")


def delete_script(request, script_id):
    if request.user.is_authenticated:
        current_script = db_script.objects.get(id=script_id)
        data = db_script_archive(user_id=current_script.user_id, script_id=script_id, team=current_script.team,
                                 supplier_name=current_script.supplier_name, script_file=current_script.script_file,
                                 proxy_file=current_script.proxy_file, servers=current_script.servers,
                                 input_field_mapping=current_script.input_field_mapping,
                                 output_field_mapping=current_script.output_field_mapping,
                                 timeout=current_script.timeout, attempt=current_script.attempt,
                                 creation_date=current_script.creation_date, last_updated=current_script.last_updated)
        data.save()
        db_script.objects.filter(id=script_id).delete()
        return JsonResponse({'data': 'success'})
    else:
        return HttpResponseRedirect("/crawl/")


def myscripts(request):
    if request.user.is_authenticated:
        db_script_query_results = db_script.objects.filter(user_id=request.user.id).order_by('creation_date').reverse()
        template = loader.get_template('crawl/myscripts.html')
        mod_data = []
        for data in db_script_query_results:
            temp_data = {}
            temp_data["script_id"] = data.id
            temp_data["script_name"] = data.supplier_name
            temp_data["creation_date"] = data.creation_date
            temp_data["last_updated"] = data.last_updated
            # temp_data["script_file"] = data.script_file
            # temp_data["proxy_file"] = data.proxy_file
            # temp_data["servers"] = data.servers
            temp_data["timeout"] = data.timeout
            temp_data["attempt"] = data.attempt
            # temp_data["input_field_mapping"] = data.input_field_mapping
            # temp_data["output_field_mapping"] = data.output_field_mapping
            mod_data.append(temp_data)
        context = {"db_script_query_results": mod_data}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")


def update_myscripts_status(request):
    if request.user.is_authenticated:
        db_script_query_results = db_script.objects.filter(user_id=request.user.id).order_by('creation_date').reverse()
        mod_data = []
        for data in db_script_query_results:
            temp_data = {}
            temp_data["script_id"] = data.id
            temp_data["script_name"] = data.supplier_name
            temp_data["creation_date"] = data.creation_date
            temp_data["last_updated"] = data.last_updated
            # temp_data["script_file"] = data.script_file
            # temp_data["proxy_file"] = data.proxy_file
            # temp_data["servers"] = data.servers
            temp_data["timeout"] = data.timeout
            temp_data["attempt"] = data.attempt
            # temp_data["input_field_mapping"] = data.input_field_mapping
            # temp_data["output_field_mapping"] = data.output_field_mapping
            mod_data.append(temp_data)
        context = {"db_script_query_results": mod_data}
        return JsonResponse({'data': mod_data})


# def edit_script(request, script_id):
#     if request.user.is_authenticated:
#         incident = get_object_or_404(db_script, pk=script_id)
#         if request.POST:
#             form = db_edit_scriptForm(request.session['user_id'], request.session['team'], request.POST, request.FILES,
#                                       instance=incident)
#             if form.is_valid():
#                 form.save()
#                 request.session['msg_data'] = 'create_supplier'
#                 request.session['supplier_name'] = request.POST['supplier_name']
#                 return HttpResponseRedirect("/crawl/myscripts")
#         else:
#             # form = db_scriptForm(instance=incident)
#             form = db_edit_scriptForm(request.session['user_id'], request.session['team'], instance=incident)
#         return render(request, 'crawl/edit_script.html', {
#             'form': form
#         })
#     else:
#         return HttpResponseRedirect("/crawl/")


def edit_script3(request, script_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            p = get_object_or_404(db_script, pk=script_id)
            form = db_scriptForm(request.session['user_id'], request.session['team'], request.POST, request.FILES,
                                 instance=p)
            # form = db_edit_scriptForm(request.session['user_id'], request.session['team'], request.POST, request.FILES, instance=p)
            # print(form.supplier_name)
            print(request.POST['supplier_name'])
            print(request.POST['script_file'])
            print(request.POST['proxy_file'])
            print(request.POST['servers'])
            if form.is_valid():
                # form.save()
                new_batch = form.save()
                print("yeahhh")
                print(new_batch.supplier_name)
                request.session['msg_data'] = 'create_supplier'
                request.session['supplier_name'] = request.POST['supplier_name']
                # user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                # start the task in the background
                # General Syntax -> schedule_batch.delay(teamName, batchName, inputFile, scriptName)
                # schedule_batch.delay(new_batch.id, new_batch.batch_name, new_batch.team, new_batch.input_file.name, new_batch.script_name, request.session['user_id'])
                return HttpResponseRedirect("/crawl/dashboard")
            else:
                return HttpResponseRedirect("/crawl/dashboard")
        else:
            # current_script = db_script.objects.get(id=script_id)
            # script_data = {}
            # script_data["script_id"] = current_script.id
            # script_data["script_name"] = current_script.supplier_name
            # script_data["creation_date"] = current_script.creation_date
            # script_data["last_updated"] = current_script.last_updated
            # script_data["script_file"] = current_script.script_file
            # script_data["proxy_file"] = current_script.proxy_file
            # script_data["servers"] = current_script.servers
            # script_data["timeout"] = current_script.timeout
            # script_data["attempt"] = current_script.attempt
            # script_data["input_field_mapping"] = current_script.input_field_mapping
            # script_data["output_field_mapping"] = current_script.output_field_mapping
            # p = get_object_or_404(db_script, pk=script_id)
            p = db_script.objects.get(id=script_id)[0]
            form = db_scriptForm(request.session['user_id'], request.session['team'], request.POST, request.FILES,
                                 instance=p, initial={'supplier_name': p["script_name"],
                                                      'script_file': p["script_file"],
                                                      'proxy_file': p["proxy_file"],
                                                      'servers': p["servers"],
                                                      'timeout': p["timeout"],
                                                      'attempt': p["attempt"],
                                                      'input_field_mapping': p["input_field_mapping"],
                                                      'output_field_mapping': p["output_field_mapping"],
                                                      })
            # form = db_scriptForm(request.session['user_id'], request.session['team'], script_data,
            #                           initial={'supplier_name': script_data["script_name"],
            #                                    'script_file': script_data["script_file"],
            #                                    'proxy_file': script_data["proxy_file"],
            #                                    'servers': script_data["servers"],
            #                                    'timeout': script_data["timeout"],
            #                                    'attempt': script_data["attempt"],
            #                                    'input_field_mapping': script_data["input_field_mapping"],
            #                                    'output_field_mapping': script_data["output_field_mapping"],
            #                                    })
            return render(request, 'crawl/edit_script.html', {
                'form': form,
            })
    else:
        return HttpResponseRedirect("/crawl/")


def edit_script2(request, script_id):
    if request.user.is_authenticated:
        current_script = db_script.objects.get(id=script_id)

        template = loader.get_template('crawl/edit_script.html')
        script_data = {}
        script_data["script_id"] = current_script.id
        script_data["script_name"] = current_script.supplier_name
        script_data["creation_date"] = current_script.creation_date
        script_data["last_updated"] = current_script.last_updated
        script_data["script_file"] = current_script.script_file
        script_data["proxy_file"] = current_script.proxy_file
        script_data["servers"] = current_script.servers
        script_data["timeout"] = current_script.timeout
        script_data["attempt"] = current_script.attempt

        context = {"script_data": script_data}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect("/crawl/")


def update_recent_requests(request, batch_id):
    if request.user.is_authenticated:
        batch_name = db_batch.objects.get(id=batch_id).batch_name
        script_id = db_batch.objects.get(id=batch_id).script_name_id
        team_name = db_script.objects.get(id=script_id).team
        server_details = db_script.objects.get(id=script_id).servers
        server_details = server_details.split('|')
        server_details = [[temp.split(':')[0], temp.split(':')[1], temp.split(':')[2]] for temp in server_details]
        recent_requests = []
        for each_server in server_details:
            try:
                # print('Fetching Requests: ', batch_name, script_id, team_name, each_server[0])
                server_name = each_server[0]
                requests_log = '\\\\' + str(server_name) + '\\e$\\Panacea\\Team_data\\' + str(
                    team_name) + '\\' + str(batch_name) + '\\request.log'
                # print(requests_log)
                if os.path.exists(requests_log):
                    line = tail(open(requests_log), 1)
                    if line:
                        recent_requests.append(str(server_name) + ":" + line[1].split('\t')[2])
            except Exception as e:
                print('Unable to fetch from:', batch_name, each_server[0])
        return JsonResponse({'data': '<br>'.join(recent_requests)})
    else:
        return HttpResponseRedirect("/crawl/")


def update_completion_estimate(request, batch_id):
    if request.user.is_authenticated:
        current_batch = db_batch.objects.get(id=batch_id)
        batch_run = db_batch_run.objects.filter(batch_id=batch_id).order_by('creation_date').reverse()
        if batch_run:
            batch_run = batch_run[0]
        remaining_input = int(batch_run.input_count) - int(batch_run.completion)
        cd = batch_run.creation_date.replace(tzinfo=None)
        time_elapsed = (datetime.datetime.now() - cd).seconds
        per_input = round(time_elapsed / int(batch_run.completion), 2)
        remaining_seconds = round(remaining_input * per_input, 2)
        speed = int(batch_run.completion) / time_elapsed
        eta = (datetime.datetime.now() + datetime.timedelta(0, remaining_seconds)).strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'eta': 'ETC: ' + eta,
            'speed': str(speed)
        }
        # return HttpResponse(json.dumps(data))
        return JsonResponse(data)
    else:
        return HttpResponseRedirect("/crawl/")


def analyze_proxy(request, batch_id):
    if request.user.is_authenticated:
        batch_name = db_batch.objects.get(id=batch_id).batch_name
        script_id = db_batch.objects.get(id=batch_id).script_name_id
        team_name = db_script.objects.get(id=script_id).team
        server_details = db_script.objects.get(id=script_id).servers
        server_details = server_details.split('|')
        server_details = [[temp.split(':')[0], temp.split(':')[1], temp.split(':')[2]] for temp in server_details]
        logger = get_or_create_task_logger(team_name, batch_name)
        Batch.get_proxy_analysis(batch_id, server_details, batch_name, team_name, logger)
        return JsonResponse({'msg': "", 'report_location': ""})
        # generate_batch_report2.delay(current_batch.id, current_batch.batch_name, current_batch.team,
        #                       batch_run.server_report)
    else:
        return HttpResponseRedirect("/crawl/")


def clickdata(request):
    if request.user.is_authenticated:
        return render(request, 'crawl/clickdata.html', {})
    else:
        return HttpResponseRedirect("/crawl/")


# Views related to servers

def add_new_server(request):
    if request.user.is_authenticated:
        # db_script_query_results = db_script.objects.filter(user_id=request.user.id).order_by('creation_date').reverse()
        template = loader.get_template('crawl/add_server.html')
        form = add_server(request.POST, extra=request.POST.get('extra_field_count'))
        if form.is_valid():
            print("valid!")
        else:
            form = add_server()
        return render(request, template, {'form': form})
    else:
        return HttpResponseRedirect("/crawl/")
