#!/usr/bin/python
# -*- coding: utf-8 -*-
from settings import fb_version, fb_page_id, fb_client_id, fb_client_secret
import requests

base_url = "https://graph.facebook.com/%s/" %fb_version

def get_posts():
    url = base_url + "%s/posts?limit=100&access_token=%s|%s" %(fb_page_id, fb_client_id, fb_client_secret)
    posts = requests.get(url).json()
    post_ids = []
    posts_dict = {}
    pagination = True
    while pagination:
        for post in posts['data']:
            # cheating and removing commas in the message for right now
            message = post.get('message', '').replace('\n', ' ').replace(',', ' ')
            created_time = post['created_time'].replace('T', ' ').replace('+0000', '')
            posts_dict[post['id']] = [message, created_time]
        if 'paging' in posts:
            posts = requests.get(posts['paging']['next']).json()
        else:
            pagination = False
    return posts_dict

# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments]}
def get_interactions(posts_dict):
    for post_id in posts_dict.keys():
        url = base_url + "%s?fields=likes.summary(true),shares.summary(true),comments.summary(true)&access_token=%s|%s" %(post_id, fb_client_id, fb_client_secret)
        interactions = requests.get(url).json()
        likes = 0
        shares = 0
        comments = 0
        if 'likes' in interactions:
            likes = interactions['likes']['summary']['total_count']
        if 'shares' in interactions:
            shares = interactions['shares']['count']
        if 'comments' in interactions:
            comments = interactions['comments']['summary']['total_count']
        posts_dict[post_id].append(likes)
        posts_dict[post_id].append(shares)
        posts_dict[post_id].append(comments)
    return posts_dict

