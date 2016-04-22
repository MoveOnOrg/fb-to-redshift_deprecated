#!/usr/bin/python
# -*- coding: utf-8 -*-
from settings import fb_version, fb_page_id, fb_long_token
import requests

base_url = "https://graph.facebook.com/%s/" %fb_version

# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments]}
def get_posts_and_interactions():
    url = base_url + '%s/posts?fields=message,created_time,id,likes.summary(true),comments.summary(true),shares&limit=40&access_token=%s' %(fb_page_id, fb_long_token)
    posts = requests.get(url).json()
    print(posts)
    posts_dict = {}
    pagination = True
    while pagination:
        for post in posts['data']:
            message = post.get('message', '').replace('\n', ' ').replace(',', ' ')
            created_time = post['created_time'].replace('T', ' ').replace('+0000', '')
            likes = 0
            shares = 0
            comments = 0
            if 'likes' in post:
                likes = post['likes']['summary']['total_count']
            if 'shares' in post:
                shares = post['shares']['count']
            if 'comments' in post:
                comments = post['comments']['summary']['total_count']
            posts_dict[post['id']] = [message, created_time, likes, shares, comments]
            if 'paging' in posts:
                posts = requests.get(posts['paging']['next']).json()
            else:
                pagination = False
    return posts_dict


# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments, total_reach]}
def get_total_reach(posts_dict):
    for post_id in posts_dict.keys():
        url = base_url + "%s/insights/post_impressions?period=lifetime&access_token=%s" %(post_id, fb_long_token)
        total_reach_values = requests.get(url).json()
        total_reach = 0
        if len(total_reach_values['data']) > 0 and 'values' in total_reach_values['data'][0]:
            total_reach = total_reach_values['data'][0]['values'][0]['value']
        posts_dict[post_id].append(total_reach)
    return posts_dict

def get_long_lived_token():
    user_access_token = 'add your user access token here'
    client_id = 'add your client id here'
    client_secret = 'add your client secret here'
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' %(client_id, client_secret, user_access_token)
    token = requests.get(url)
    return token.text[13:]

def get_page_access_token_from_user_token(long_user_access_token):
    url = base_url + '%s?fields=access_token&access_token=%s' %(fb_page_id, long_user_access_token)
    page_token = requests.get(url).json()   
    print(page_token['access_token'])
    
# get_page_access_token_from_user_token(get_long_lived_token())