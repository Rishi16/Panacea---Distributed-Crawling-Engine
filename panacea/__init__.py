from __future__ import absolute_import
from .celery_config import app as celery_app
import pythoncom
from crawl.Backbone import wmi
pythoncom.CoInitialize()

__all__ = ['celery_app']