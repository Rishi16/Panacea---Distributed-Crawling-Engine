import servicemanager
import win32security, win32net, win32file, win32api, win32con
from random import random
from socket import socket

import win32netcon, ntsecuritycon
import os, sys, string

def create_user(username, password, password_expires=False):
    user_info = {
        "name": username,
        "password": password,
        "priv": win32netcon.USER_PRIV_USER,
        "flags": win32netcon.UF_NORMAL_ACCOUNT | win32netcon.UF_SCRIPT,
    }

    if not password_expires:
        user_info["flags"] |= win32netcon.UF_DONT_EXPIRE_PASSWD

    win32net.NetUserAdd(None, 1, user_info)


create_user("panacea3", "eclerx#123")