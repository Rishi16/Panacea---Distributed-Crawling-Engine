from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.http import HttpResponseRedirect


# from .models import Question


def index(request):
    return HttpResponseRedirect("/crawl/")
