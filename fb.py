#!/usr/bin/python
# -*- coding: utf-8 -*-
from settings import fb_version, fb_page_id, fb_long_token, post_limit
import requests
import json
import sys
import time

base_url = "https://graph.facebook.com/%s/" %fb_version

# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments]}
def get_posts_and_interactions(interval='month'):
    
    now = int(time.time())
    if interval == 'week':
        since = now - 604800
    if interval == 'month':
        since = now - 2592000
    if interval == 'year':
        since = now - 31536000
    
    limit = post_limit
    too_many_posts_at_a_time = True

    while too_many_posts_at_a_time:
        if interval:
            url = base_url + '%s/posts?fields=message,created_time,id,likes.summary(true),comments.summary(true),shares&limit=%s&since=%s&access_token=%s' %(fb_page_id, limit, since, fb_long_token)
        else:
            url = base_url + '%s/posts?fields=message,created_time,id,likes.summary(true),comments.summary(true),shares&limit=%s&access_token=%s' %(fb_page_id, limit, fb_long_token)
        posts = requests.get(url).json()
        if 'error' in posts:
            limit = str(int(limit) - 5)
        else:
            too_many_posts_at_a_time = False

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
                try:
                    likes = post['likes']['summary']['total_count']
                except KeyError:
                    error_log = open('error_log.json','a')
                    json.dump(post, error_log, indent=4)
            if 'shares' in post:
                try:
                    shares = post['shares']['count']
                except KeyError:
                    error_log = open('error_log.json','a')
                    json.dump(post, error_log, indent=4)
            if 'comments' in post:
                try:
                    comments = post['comments']['summary']['total_count']
                except KeyError:
                    error_log = open('error_log.json','a')
                    json.dump(post, error_log, indent=4)                    
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