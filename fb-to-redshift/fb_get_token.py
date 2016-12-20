#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Get access tokens that allow us to get data from Graph API.
    See README.md for how to use.
"""

import sys
import os
local_settings_path = os.path.join(os.getcwd(),"settings.py")
if os.path.exists(local_settings_path):
    import imp
    settings = imp.load_source('settings', local_settings_path)

from settings import (
    fb_version, fb_page_id, fb_long_token, user_access_token, client_id,
    client_secret)
import requests

base_url = "https://graph.facebook.com/%s/" %fb_version

def get_long_lived_token():
    url = (
        'https://graph.facebook.com/oauth/access_token'
        '?grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
        '&fb_exchange_token=%s' %(
            client_id, client_secret, user_access_token))
    token = requests.get(url)
    return token.text[13:]

def get_page_access_token_from_user_token(long_user_access_token):
    if not user_access_token or not fb_page_id:
        raise Exception("settings fb_page_id and user_access_token must be set")
    url = base_url + '%s?fields=access_token&access_token=%s' %(
        fb_page_id, user_access_token)
    page_token = requests.get(url).json()
    if page_token.get('error'):
        print(page_token)
    else:
        print(page_token['access_token'])
    
get_page_access_token_from_user_token(get_long_lived_token())
