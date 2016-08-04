#!/usr/bin/python
# -*- coding: utf-8 -*-
from settings import fb_version, fb_page_id, fb_long_token, post_limit
import requests
import json
import sys
import time

base_url = "https://graph.facebook.com/%s/" %fb_version

# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments]}
# set interval = False to update all post data

def get_posts_and_interactions(interval='month'):
    
    now = int(time.time())
    if interval == 'week':
        since = str(now - 604800)
    if interval == 'month':
        since = str(now - 2592000)
    if interval == 'year':
        since = str(now - 31536000)
    now = str(now)
    
    limit = post_limit
    too_many_posts_at_a_time = True

    while too_many_posts_at_a_time:
        if interval:
            url = base_url + '%s/posts?fields=message,created_time,id,likes.limit(0).summary(total_count),comments.limit(0).summary(total_count),shares&limit=%s&since=%s&until=%s&access_token=%s' %(fb_page_id, limit, since, now, fb_long_token)
        else:
            url = base_url + '%s/posts?fields=message,created_time,id,likes.limit(0).summary(true),comments.limit(0).summary(true),shares&limit=%s&access_token=%s' %(fb_page_id, limit, fb_long_token)
        posts = requests.get(url).json()

        #debugging
        out_file = open('posts.json','w') #debugging
        json.dump(posts,out_file, indent=4) #debugging
        #debugging

        if 'error' in posts:
            print(str(limit) + ' is too high')
            limit = str(int(limit) - 5) # try again with a smaller request
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
            print('next page')
            posts = requests.get(posts['paging']['next']).json()
        else:
            print('last page')
            pagination = False

    return posts_dict


# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments, total_reach]}
# TODO: rewrite this as a batch request https://developers.facebook.com/docs/graph-api/making-multiple-requests
def get_total_reach(posts_dict):
    for post_id in posts_dict.keys():
        url = base_url + "%s/insights/post_impressions?period=lifetime&access_token=%s" %(post_id, fb_long_token)
        total_reach_values = requests.get(url).json()
        total_reach = 0
        if len(total_reach_values['data']) > 0 and 'values' in total_reach_values['data'][0]:
            total_reach = total_reach_values['data'][0]['values'][0]['value']
        posts_dict[post_id].append(total_reach)
    return posts_dict

#avg_completion = percentage of video watched
# this results in videos_dict = {video_id: [title, description, views, likes, reactions, comments, 10sec_views, 30sec_views, to_95_percent, length, avg_time_watched, viewers, unique_viewers]}

def get_video_stats(interval = False):
    now = int(time.time())
    if interval == 'week':
        since = str(now - 604800)
    if interval == 'month':
        since = str(now - 2592000)
    if interval == 'year':
        since = str(now - 31536000)
    now = str(now)

    limit = post_limit
    too_many_posts_at_a_time = True

    while too_many_posts_at_a_time:
        if interval:
            url = base_url + '%s/videos?title,description,created_time,length,comments.limit(0),likes.limit(0),reactions.limit(0),video_insights{values,name}&limit=%s&since=%s&until=%s&access_token=%s' %(fb_page_id, limit, since, now, fb_long_token)
        else:
            url = base_url + '%s/videos?title,description,created_time,length,comments.limit(0),likes.limit(0),reactions.limit(0),video_insights{values,name}&limit=%s&access_token=%s' %(fb_page_id, limit, fb_long_token)
        videos = requests.get(url).json()
        if 'error' in videos:
            print(str(limit) + ' is too high')
            limit = str(int(limit) - 5) # try again with a smaller request
        else:
            too_many_posts_at_a_time = False

    videos_dict = {}

    out_file = open('videos.json','w')
    json.dump(videos,out_file, indent=4)

    # pagination = True

    # while pagination:
    #     for post in posts['data']:
    #         message = post.get('message', '').replace('\n', ' ').replace(',', ' ')
    #         created_time = post['created_time'].replace('T', ' ').replace('+0000', '')
    #         likes = 0
    #         shares = 0
    #         comments = 0
    #         if 'likes' in post:
    #             try:
    #                 likes = post['likes']['summary']['total_count']
    #             except KeyError:
    #                 error_log = open('error_log.json','a')
    #                 json.dump(post, error_log, indent=4)
    #         if 'shares' in post:
    #             try:
    #                 shares = post['shares']['count']
    #             except KeyError:
    #                 error_log = open('error_log.json','a')
    #                 json.dump(post, error_log, indent=4)
    #         if 'comments' in post:
    #             try:
    #                 comments = post['comments']['summary']['total_count']
    #             except KeyError:
    #                 error_log = open('error_log.json','a')
    #                 json.dump(post, error_log, indent=4)                    
    #         posts_dict[post['id']] = [message, created_time, likes, shares, comments]
    #     if 'paging' in posts:
    #         posts = requests.get(posts['paging']['next']).json()
    #     else:
    #         pagination = False

    return videos_dict

# TODO: get shares and reactions separately in a batch request, count them, and add them to the dict
# TODO: get reach for all the videos

#for dev only
#get_video_stats()