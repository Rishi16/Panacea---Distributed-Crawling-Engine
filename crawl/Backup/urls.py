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
    path('script', views.script, name='script'),
    path('dashboard', views.dashboard, name='dashboard'),
    url(r'^(?P<batch_id>[0-9]+)/$', views.batch, name='batch'),
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