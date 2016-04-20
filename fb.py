#!/usr/bin/python
# -*- coding: utf-8 -*-
from settings import fb_token, fb_version, fb_page_id
import requests
import sys

base_url = "https://graph.facebook.com/%s/" %fb_version

def get_posts():
    url = base_url + "%s/posts?limit=100&access_token=%s" %(fb_page_id, fb_token)
    posts = requests.get(url).json()
    post_ids = []
    posts_dict = {}
    pagination = True
    while pagination:
        for post in posts['data']:
            # figure out dumb encoding bs
            # message = post['message'].replace('\n', ' ')
            # message = message.encode('utf-8')
            message = ' '
            created_time = post['created_time'].replace('T', ' ')
            posts_dict[post['id']] = [message, created_time]
        if posts.has_key('paging'):
            posts = requests.get(posts['paging']['next']).json()
        else:
            pagination = False
    return posts_dict

# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments]}
def get_interactions(posts_dict):
    for post_id in posts_dict.keys():
        url = base_url + "%s?fields=likes.summary(true),shares.summary(true),comments.summary(true)&access_token=%s" %(post_id, fb_token)
        interactions = requests.get(url).json()
        likes = interactions.get('likes', 0)
        if likes != 0:
            likes = interactions['likes']['summary']['total_count']
        shares = interactions.get('shares', 0)
        if shares != 0:
            shares = shares['count']
        comments = interactions.get('comments', 0)
        if comments != 0:
            comments = interactions['comments']['summary']['total_count']
        posts_dict[post_id].append(likes)
        posts_dict[post_id].append(shares)
        posts_dict[post_id].append(comments)
    return posts_dict



