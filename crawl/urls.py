from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    path('new', views.new, name='new'),
    path('mybatches', views.mybatches, name='mybatches'),
    path('mybatchestop', views.mybatchestop, name='mybatchestop'),
    url(r'^update_recent_requests/(?P<batch_id>\d+)/$', views.update_recent_requests, name='update_recent_requests'),
    url(r'^update_completion_estimate/(?P<batch_id>\d+)/$', views.update_completion_estimate, name='update_completion_estimate'),
    url(r'^edit_batch/(?P<batch_id>\d+)/$', views.edit_batch, name='edit_batch'),
    url(r'^delete_batch/(?P<batch_id>\d+)/$', views.delete_batch, name='delete_batch'),
    url(r'^batch_proxy/(?P<batch_id>\d+)/$', views.batch_proxy, name='batch_proxy'),
    url(r'^batch_logs/(?P<batch_id>\d+)/$', views.batch_logs, name='batch_logs'),
    url(r'^analyze_proxy/(?P<batch_id>\d+)/$', views.analyze_proxy, name='analyze_proxy'),
    path('myscripts', views.myscripts, name='myscripts'),
    path('script', views.script, name='script'),
    url(r'^edit_script/(?P<script_id>\d+)/$', views.edit_script, name='edit_script'),
    url(r'^delete_script/(?P<script_id>\d+)/$', views.delete_script, name='delete_script'),
    path('dashboard', views.dashboard, name='dashboard'),
    # path('update_batch_status', views.update_batch_status, name='update_batch_status'),
    path('update_mybatches_status', views.update_mybatches_status, name='update_mybatches_status'),
    path('update_myscripts_status', views.update_myscripts_status, name='update_myscripts_status'),
    path('clickdata', views.clickdata, name='clickdata'),
    url(r'^(?P<batch_id>[0-9]+)/$', views.batch, name='batch'),
    url(r'^update_batch_status/(?P<batch_id>\d+)/$', views.update_batch_status, name='update_batch_status'),
    url(r'^change_batch_status/(?P<batch_id>\d+)/(?P<status>\D+)$', views.change_batch_status, name='change_batch_status'),
    url(r'^generate_report/(?P<batch_id>\d+)/$', views.generate_report, name='generate_report'),
    url(r'^generate_run_report/(?P<batch_id>\d+)/(?P<batch_run_id>\d+)$', views.generate_report, name='generate_report'),
    url(r'^download_report/(?P<batch_id>\d+)(\/\?\d+)?/$', views.download_report, name='download_report'),
    url(r'^servers/(?P<batch_id>\d+)/$', views.servers, name='servers'),
    path('add_server', views.add_new_server, name='add_new_server'),
    # ex: /polls/5/
    # path('<int:question_id>/', views.detail, name='detail'),
    # # ex: /polls/5/results/
    # path('<int:question_id>/results/', views.results, name='results'),
    # # ex: /polls/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]

# urlpatterns += patterns('',
#    (r'^(?P<page_alias>.+?)/$', 'views.batch'),
# )
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)