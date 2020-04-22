"""
Author: Harsh Dubey
Windows Remote Connection Library: WMI

(Please feel free to use this code for personal use only without changing it or its functionality)
"""

import os

current_path = ''
backbone_path = ''
team_in_system = []
team_status = {}
batch_in_system = {}
batch_status = 'notstarted'
property = ''

def init():
    global current_path
    global backbone_path
    # current_path = os.path.dirname(os.path.abspath(__file__))
    current_path = 'E:/Panacea'
    backbone_path = 'E:/Harsh/django_projects/panacea/crawl/Backbone'