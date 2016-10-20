#!/usr/bin/python
# -*- coding: utf-8 -*-
""" All the functions that work with the Graph API to get data.
"""

from settings import fb_version, fb_page_id, fb_long_token, post_limit, time_series_start_date
import requests
import json
import sys
import time
from datetime import datetime

base_url = "https://graph.facebook.com/%s/" %fb_version


def log_error(content,logfile):
    error_log = open(logfile,'a')
    error_log.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    json.dump(content, error_log, indent=4)
    error_log.close()

# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments]}
# set interval = False to update all post data

def get_posts_and_interactions(interval=False):
    
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

        if 'error' in posts:
            log_error(posts,'error_log.json')
            if posts['error']['code'] == 1:
                print(str(limit) + ' is too high')
                limit = str(int(limit) - 5) # try again with a smaller request
            elif posts['error']['code'] == 190:
                print('bad access_token! see error log for details')
                break
            else:
                print('API error code ' + str(posts['error']['code']))
                break
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
                    log_error(post,'error_log.json')
            if 'shares' in post:
                try:
                    shares = post['shares']['count']
                except KeyError:
                    log_error(post,'error_log.json')
            if 'comments' in post:
                try:
                    comments = post['comments']['summary']['total_count']
                except KeyError:
                    log_error(post,'error_log.json')
            posts_dict[post['id']] = [message, created_time, likes, shares, comments]
        if 'paging' in posts:
            posts = requests.get(posts['paging']['next']).json()
        else:
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

# this results in videos_dict = {video_id: [title, description, created_time, length, likes, comments, reactions, shares, insights['total_video_impressions_unique'], insights['total_video_view_total_time'], insights['total_video_views'],insights['total_video_views_unique'], insights['total_video_10s_views_unique'], insights['total_video_30s_views_unique'], insights['total_video_complete_views'], avg_completion]}

def get_video_stats(interval = False, video_lab = False, list_id = None):
    now = int(time.time())
    if interval == 'week':
        since = str(now - 604800)
    if interval == 'month':
        since = str(now - 2592000)
    if interval == 'year':
        since = str(now - 31536000)
    now = str(now)

    limit = post_limit
    too_many_videos_at_a_time = True

    while too_many_videos_at_a_time:

        if video_lab:
            if interval:
                url = base_url + '%s/?fields=videos{title,description,created_time,length,likes.limit(0).summary(total_count),comments.limit(0).summary(total_count),reactions.limit(0).summary(total_count),video_insights}&limit=%s&since=%s&until=%s&access_token=%s' %(list_id, limit, since, now, fb_long_token)
            else:
                url = base_url + '%s/?fields=videos{title,description,created_time,length,likes.limit(0).summary(total_count),comments.limit(0).summary(total_count),reactions.limit(0).summary(total_count),video_insights}&limit=%s&access_token=%s' %(list_id, limit, fb_long_token)
        else:
            if interval:
                url = base_url + '%s/videos?fields=title,description,created_time,length,comments.limit(0).summary(total_count),likes.limit(0).summary(total_count),reactions.limit(0).summary(total_count),video_insights{values,name}&limit=%s&since=%s&until=%s&access_token=%s' %(fb_page_id, limit, since, now, fb_long_token)
            else:
                url = base_url + '%s/videos?fields=title,description,created_time,length,comments.limit(0).summary(total_count),likes.limit(0).summary(total_count),shares.limit(0).summary(total_count),reactions.limit(0).summary(total_count),video_insights{values,name}&limit=%s&access_token=%s' %(fb_page_id, limit, fb_long_token)

        videos = requests.get(url).json()
        if 'error' in videos:
            log_error(videos,'error_log.json')
            if videos['error']['code'] == 1:
               print(str(limit) + ' is too high')
               limit = str(int(limit) - 5) # try again with a smaller request
            elif videos['error']['code'] == 190:
               print('bad access_token! see error log for details')
               break
            else:
               print('API error code ' + str(videos['error']['code']))
               break
        else:
            too_many_videos_at_a_time = False

    videos_dict = {}

    pagination = True

    if video_lab:
        videos = videos['videos']

    while pagination:
        for video in videos['data']:
            title = video.get('title', '').replace('\n', ' ').replace(',', ' ')
            description = video.get('description', '').replace('\n', ' ').replace(',', ' ').replace('"','')
            created_time = video['created_time'].replace('T', ' ').replace('+0000', '')
            length = video['length']
            likes = 0
            comments = 0
            reactions = 0
            if 'likes' in video:
                try:
                    likes = video['likes']['summary']['total_count']
                except KeyError:
                    log_error(video,'error_log.json')
            if 'comments' in video:
                try:
                    comments = video['comments']['summary']['total_count']
                except KeyError:
                    log_error(video,'error_log.json')
            if 'reactions' in video:
                try:
                    reactions = video['reactions']['summary']['total_count']
                except KeyError:
                    log_error(video,'error_log.json')
            
            insights = {}
            no_insights = False
            try:
                insights_data = video['video_insights']['data']
            except KeyError:
                no_insights = True
            for insight in insights_data:
                insights[insight['name']] = insight['values'][0]['value']
            if no_insights:
                videos_dict[video['id']] = [title, description, created_time, length, likes, comments, reactions]
            else:
                try:
                    shares = insights['total_video_stories_by_action_type']['share']
                except KeyError:
                    shares = 0
                avg_completion = round(float(insights['total_video_avg_time_watched']) / length / 1000.0, 3)
                videos_dict[video['id']] = [title, description, created_time, length, likes, comments, reactions, shares, insights['total_video_impressions_unique'], insights['total_video_view_total_time'], insights['total_video_views'],insights['total_video_views_unique'], insights['total_video_10s_views_unique'], insights['total_video_30s_views_unique'], insights['total_video_complete_views'], avg_completion]
        try: 
            videos = requests.get(videos['paging']['next']).json()
        except KeyError:
            pagination = False
        # end while

    return videos_dict

def get_video_time_series(start_date = time_series_start_date):
    
    since = int(datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp())
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    too_many_videos_at_a_time = True

    limit = post_limit

    while too_many_videos_at_a_time:
        url = base_url + '%s/videos?fields=title,created_time,video_insights{values,name}&limit=%s&since=%s&access_token=%s' %(fb_page_id, limit, since, fb_long_token)

        videos = requests.get(url).json()
        if 'error' in videos:
            log_error(videos,'error_log.json')
            if videos['error']['code'] == 1:
               print(str(limit) + ' is too high')
               limit = str(int(limit) - 5) # try again with a smaller request
            elif videos['error']['code'] == 190:
               print('bad access_token! see error log for details')
               break
            else:
               print('API error code ' + str(videos['error']['code']))
               break
        else:
            too_many_videos_at_a_time = False

    videos_dict = {}

    pagination = True

    while pagination:
        for video in videos['data']:
            title = video.get('title', '').replace('\n', ' ').replace(',', ' ')
            created_time = video['created_time'].replace('T', ' ').replace('+0000', '')            
            insights = {}
            no_insights = False
            try:
                insights_data = video['video_insights']['data']
            except KeyError:
                no_insights = True
            for insight in insights_data:
                insights[insight['name']] = insight['values'][0]['value']
            if no_insights:
                videos_dict[video['id']] = [title, created_time, now]
            else:
                videos_dict[video['id']] = [title, created_time, now, insights['total_video_views'],insights['total_video_views_unique'], insights['total_video_10s_views_unique']]
        try: 
            videos = requests.get(videos['paging']['next']).json()
        except KeyError:
            pagination = False
        # end while

    return videos_dict
