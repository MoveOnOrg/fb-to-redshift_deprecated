#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Get tokens that allow us to get page data from Graph API.
    See README.md for how to get an immortal token.
"""

from settings import (
    fb_version, fb_page_id, fb_long_token, user_access_token, client_id,
    client_secret)
import requests

base_url = "https://graph.facebook.com/%s/" %fb_version

def get_long_lived_token():
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' %(client_id, client_secret, user_access_token)
    token = requests.get(url)
    return token.text[13:]

def get_page_access_token_from_user_token(long_user_access_token):
    url = base_url + '%s?fields=access_token&access_token=%s' %(fb_page_id, user_access_token)
    page_token = requests.get(url).json()
    print(page_token['access_token'])
    
get_page_access_token_from_user_token(get_long_lived_token())