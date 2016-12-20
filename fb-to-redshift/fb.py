#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Functions that call the Graph API to get post and video data
    and parse the response.
"""

import sys
import os
local_settings_path = os.path.join(os.getcwd(),"settings.py")
if os.path.exists(local_settings_path):
    import imp
    settings = imp.load_source('settings', local_settings_path)

from settings import (
    fb_version, fb_page_id, fb_long_token, post_limit, time_series_start_date)
import requests
import json
import sys
from time import gmtime, strftime, time
from datetime import datetime

base_url = "https://graph.facebook.com/%s/" %fb_version
def log_error(content,logfile):
    error_log = open(logfile,'a')
    error_log.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    json.dump(content, error_log, indent=4)
    error_log.close()

def get_posts_and_interactions(interval=False):
    """ Retrieve post data for a specific Facebook Page from a time
        period optionally limited by the 'interval' parameter.
        Return a dictionary with post ID as key and list of post 
        data as the value.
    """
    
    now = int(time())
    if interval == 'week':
        since = str(now - 604800)
    if interval == 'month':
        since = str(now - 2592000)
    if interval == 'year':
        since = str(now - 31536000)
    now = str(now)    
    limit = post_limit
    too_many_posts_at_a_time = True

    # If you try to grab too much data at once, the Graph API 
    # returns an error. This script will keep trying to grab 
    # incrementally smaller amounts of data until it succeeds
    # or it runs out of chances.

    while too_many_posts_at_a_time and int(limit) > 0:
        # Edit these URLs to change what data you get from the API.
        # Use the Facebook Graph API explorer to test new URLs.    
        if interval:
            url = (base_url +
                '%s/posts?fields=message,created_time,id,'
                'likes.limit(0).summary(total_count),'
                'comments.limit(0).summary(total_count),'
                'shares,'
                'insights.metric(post_impressions,post_consumptions_by_type)'
                '{values,name}'
                '&limit=%s&since=%s&until=%s&access_token=%s'
                %(fb_page_id,limit, since, now, fb_long_token))
        else:
            url = (base_url +
                '%s/posts?fields=message,created_time,id,'
                'likes.limit(0).summary(true),'
                'comments.limit(0).summary(true),'
                'shares,'
                'insights.metric(post_impressions,post_consumptions_by_type)'
                '{values,name}'
                '&limit=%s&access_token=%s'
                %(fb_page_id, limit, fb_long_token))
        
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

    if int(limit) <= 0:
        print("Failed to retrieve post data. Logged errors to error_log.json")
        return False

    else:
        posts_dict = {}
        pagination = True

        # parse the response
        while pagination:
            for post in posts['data']:
                message = post.get('message', '').replace('\n',
                    ' ').replace(',', ' ')
                created_time = post['created_time'].replace('T',
                    ' ').replace('+0000', '')
                likes = post.get('likes', {}).get('summary',
                    {}).get('total_count', 0)
                shares = post.get('shares', {}).get('count', 0)
                comments = post.get('comments', {}).get('summary',
                    {}).get('total_count', 0)
                insights = {}
                try:
                    insights_data = post['insights']['data']
                    for insight in insights_data:
                        insights[insight['name']] = insight['values'][0]['value']
                    impressions = insights.get('post_impressions', 0)
                    link_clicks = insights.get('post_consumptions_by_type',
                        {}).get('link clicks', 0)
                    posts_dict[post['id']] = [
                        message,
                        created_time,
                        likes,
                        shares,
                        comments,
                        impressions,
                        link_clicks
                        ] # this list and the next must change if the URLS do
                except KeyError:
                    posts_dict[post['id']] = [
                        message,
                        created_time,
                        likes,
                        shares,
                        comments
                        ]
            if 'paging' in posts:
                posts = requests.get(posts['paging']['next']).json()
            else:
                pagination = False

        print("Retrieved data for %s posts" %str(len(posts_dict)))
        return posts_dict

def get_video_stats(interval=False, list_id=False):
    """ Retrieve video statistics for a specific Facebook Page from
        a time period optionally limited by the 'interval' parameter.
        If a list_id is passed to this function the results are limited
        to the videos on that list. Return a dictionary with video ID
        as key and a list of video data as the value.
    """
    now = int(time())
    if interval == 'week':
        since = str(now - 604800)
    if interval == 'month':
        since = str(now - 2592000)
    if interval == 'year':
        since = str(now - 31536000)
    now = str(now)
    limit = post_limit
    too_many_videos_at_a_time = True

    while too_many_videos_at_a_time and int(limit) > 0:
        if list_id:
            if interval:
                url = (
                    base_url +
                    '%s/?fields=videos{title,description,created_time,length,'
                    'likes.limit(0).summary(total_count),'
                    'comments.limit(0).summary(total_count),'
                    'reactions.limit(0).summary(total_count),'
                    'video_insights}'
                    '&limit=%s&since=%s&until=%s&access_token=%s' 
                    %(list_id, limit, since, now, fb_long_token))
            else:
                url = (
                    base_url +
                    '%s/?fields=videos{title,description,created_time,length,'
                    'likes.limit(0).summary(total_count),'
                    'comments.limit(0).summary(total_count),'
                    'reactions.limit(0).summary(total_count),'
                    'video_insights}'
                    '&limit=%s&access_token=%s' 
                    %(list_id, limit, fb_long_token))
        else:
            if interval:
                url = (
                    base_url + 
                    '%s/videos?fields=title,description,created_time,length,'
                    'comments.limit(0).summary(total_count),'
                    'likes.limit(0).summary(total_count),'
                    'reactions.limit(0).summary(total_count),'
                    'video_insights{values,name}'
                    '&limit=%s&since=%s&until=%s&access_token=%s' 
                    %(fb_page_id, limit, since, now, fb_long_token))
            else:
                url = (
                    base_url + 
                    '%s/videos?fields=title,description,created_time,length,'
                    'comments.limit(0).summary(total_count),'
                    'likes.limit(0).summary(total_count),'
                    'reactions.limit(0).summary(total_count),'
                    'video_insights{values,name}'
                    '&limit=%s&access_token=%s' 
                    %(fb_page_id, limit, fb_long_token))

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

    if int(limit) <= 0:
        print("Failed to retrieve video data. Logged errors to error_log.json")
        return False
    else:
        videos_dict = {}
        pagination = True
        if list_id:
            videos = videos['videos']
        while pagination:
            for video in videos['data']:
                title = video.get('title', '').replace('\n', ' ').replace(',', ' ')
                description = video.get('description', '').replace('\n',
                    ' ').replace(',', ' ').replace('"','')
                created_time = video['created_time'].replace('T',
                    ' ').replace('+0000', '')
                length = video['length']
                likes = video.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = video.get('comments', {}).get('summary',
                    {}).get('total_count', 0)
                reactions = video.get('reactions', {}).get('summary',
                    {}).get('total_count', 0)
                
                insights = {}
                try:
                    insights_data = video['video_insights']['data']
                except KeyError:
                    videos_dict[video['id']] = [title, description, created_time,
                    length, likes, comments, reactions]
                else:
                    for insight in insights_data:
                        insights[insight['name']] = insight['values'][0]['value']
                    shares = insights.get('total_video_stories_by_action_type',
                        {}).get('share', 0)
                    page_owned_views = insights.get(
                        'total_video_views_by_distribution_type',{}).get(
                        'page_owned',0)
                    shared_views = insights.get(
                        'total_video_views_by_distribution_type',{}).get(
                        'shared',0)
                    avg_sec_watched = round(float(
                        insights['total_video_avg_time_watched'])/1000.0, 3)
                    avg_completion = round(float(
                        insights['total_video_avg_time_watched'])/length/1000.0, 3)
                    videos_dict[video['id']] = [
                        title, description, created_time,
                        length, likes, comments, reactions, shares, 
                        insights['total_video_impressions_unique'],
                        insights['total_video_view_total_time'], 
                        insights['total_video_views'],
                        insights['total_video_views_unique'],
                        insights['total_video_10s_views_unique'],
                        insights['total_video_30s_views_unique'], 
                        insights['total_video_complete_views'],
                        avg_sec_watched, avg_completion,
                        page_owned_views, shared_views,
                        insights['total_video_views_autoplayed'],
                        insights['total_video_views_clicked_to_play'],
                        insights['total_video_views_organic'],
                        insights['total_video_views_organic_unique'],
                        insights['total_video_views_paid'],
                        insights['total_video_views_paid_unique'],
                        insights['total_video_views_sound_on'],
                        insights['total_video_complete_views'],
                        insights['total_video_complete_views_unique'],
                        insights['total_video_complete_views_auto_played'],
                        insights['total_video_complete_views_clicked_to_play'],
                        insights['total_video_complete_views_organic'],
                        insights['total_video_complete_views_organic_unique'],
                        insights['total_video_complete_views_paid'],
                        insights['total_video_complete_views_paid_unique'],
                        insights['total_video_10s_views_auto_played'],
                        insights['total_video_10s_views_clicked_to_play'],
                        insights['total_video_10s_views_organic'],
                        insights['total_video_10s_views_paid'],
                        insights['total_video_10s_views_sound_on'],
                        insights['total_video_avg_time_watched'],
                        insights['total_video_view_total_time_organic'],
                        insights['total_video_view_total_time_paid'],
                        insights['total_video_impressions'],
                        insights['total_video_impressions_paid_unique'],
                        insights['total_video_impressions_paid'],
                        insights['total_video_impressions_organic_unique'],
                        insights['total_video_impressions_organic'],
                        insights['total_video_impressions_viral_unique'],
                        insights['total_video_impressions_viral'],
                        insights['total_video_impressions_fan_unique'],
                        insights['total_video_impressions_fan'],
                        insights['total_video_impressions_fan_paid_unique'],
                        insights['total_video_impressions_fan_paid']]   
            try: 
                videos = requests.get(videos['paging']['next']).json()
            except KeyError:
                pagination = False
            # end while

    print("Retrieved data for %s videos" %str(len(videos_dict)))
    return videos_dict

def get_video_time_series(start_date = time_series_start_date):
    """ Retrieve video statistics for a specific Facebook Page from
        a time period optionally limited by time_series_start_date.
        Return a dictionary with video ID as key and a list of video 
        data as the value.
    """
    
    since = int(datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp())
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    too_many_videos_at_a_time = True
    limit = post_limit

    while too_many_videos_at_a_time and int(limit) > 0:
        url = (
            base_url +
            '%s/videos?fields=title,created_time,video_insights{values,name},'
            'comments.limit(0).summary(total_count),'
            'likes.limit(0).summary(total_count),'
            'reactions.limit(0).summary(total_count)'
            '&limit=%s&since=%s&access_token=%s' 
            %(fb_page_id, limit, since, fb_long_token))

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
    
    if int(limit) <= 0:
        print("Failed to retrieve video time series data. Logged errors to error_log.json")
        return False
    else:
        videos_dict = {}
        pagination = True
        while pagination:
            for video in videos['data']:
                title = video.get('title', '').replace('\n', ' ').replace(',', ' ')
                created_time = video['created_time'].replace('T', ' ').replace('+0000', '')
                likes = video.get('likes', {}).get('summary', {}).get('total_count', 0)
                comments = video.get('comments', {}).get('summary',
                    {}).get('total_count', 0)
                reactions = video.get('reactions', {}).get('summary',
                    {}).get('total_count', 0)          
                insights = {}
                try:
                    insights_data = video['video_insights']['data']
                except KeyError:
                    videos_dict[video['id']] = [title, created_time, now, likes, comments, reactions]
                else:
                    for insight in insights_data:
                        insights[insight['name']] = insight['values'][0]['value']
                    shares = insights.get('total_video_stories_by_action_type',
                        {}).get('share', 0)               
                    videos_dict[video['id']] = [
                        title, created_time, now,
                        likes, comments, reactions,
                        insights['total_video_views'],
                        insights['total_video_views_unique'],
                        insights['total_video_10s_views_unique'],
                        insights['total_video_impressions_unique'],
                        insights['total_video_view_total_time'],
                        shares
                        ]
            try: 
                videos = requests.get(videos['paging']['next']).json()
            except KeyError:
                pagination = False
            # end while

    return videos_dict

def get_video_views_demographics(interval = False, list_id = False):
    """ Retrieve video viewer demographics for a specific Facebook Page
        from a time period optionally limited by the 'interval'
        parameter. If a list_id is passed to this function the results
        are limited to the videos on that list. Return a dictionary
        with video ID as key and a list of video data as the value.
    """
    now = int(time())
    if interval == 'week':
        since = str(now - 604800)
    if interval == 'month':
        since = str(now - 2592000)
    if interval == 'year':
        since = str(now - 31536000)
    now = str(now)
    limit = post_limit
    too_many_videos_at_a_time = True

    while too_many_videos_at_a_time and int(limit) > 0:
        if list_id:
            if interval:
                url = (
                    base_url +
                    '%s/?fields=videos{video_insights.metric('
                    'total_video_view_time_by_region_id,'
                    'total_video_view_time_by_age_bucket_and_gender)}'
                    '&limit=%s&since=%s&until=%s&access_token=%s'
                    %(list_id, limit, since, now, fb_long_token))
            else:
                url = (
                    base_url +
                    '%s/?fields=videos{video_insights.metric('
                    'total_video_view_time_by_region_id,'
                    'total_video_view_time_by_age_bucket_and_gender)}'
                    '&limit=%s&access_token=%s' 
                    %(list_id, limit, fb_long_token))
        else:
            if interval:
                url = (
                    base_url + 
                    '%s/videos?fields=video_insights.metric('
                    'total_video_view_time_by_region_id,'
                    'total_video_view_time_by_age_bucket_and_gender){values,name}'
                    '&limit=%s&since=%s&until=%s&access_token=%s' 
                    %(fb_page_id, limit, since, now, fb_long_token))
            else:
                url = (
                    base_url +
                    '%s/videos?fields=video_insights.metric('
                    'total_video_view_time_by_region_id,'
                    'total_video_view_time_by_age_bucket_and_gender){values,name}'
                    '&limit=%s&access_token=%s' 
                    %(fb_page_id, limit, fb_long_token))

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
    
    if int(limit) <= 0:
        print("Failed to retrieve video demographics data. Logged errors to error_log.json")
        return False
    else:
        videos_dict = {}
        pagination = True
        if list_id:
            videos = videos['videos']

        while pagination:
            for video in videos['data']:
                insights = {}
                no_insights = False
                try:
                    insights_data = video['video_insights']['data']
                except KeyError:
                    videos_dict[video['id']] = []
                else:
                    for insight in insights_data:
                        insights[insight['name']] = insight['values'][0]['value']
                    try:
                        regions = insights['total_video_view_time_by_region_id']
                        regions_data = [] # 45 regions
                        for key,value in regions.items():
                            regions_data.append(key)
                            regions_data.append(value)
                    except KeyError:
                        regions_data = ['' for x in range(45)]
                        print("no regions views data for video %s" %video['id'])
                    try:
                        age_gender_dict = insights['total_video_view_time_by_age_bucket_and_gender']
                        age_gender_buckets = ['U.13-17','U.18-24','U.25-34','U.35-44',
                            'U.45-54','U.55-64','U.65+','F.13-17','F.18-24','F.25-34',
                            'F.35-44','F.45-54','F.55-64','F.65+','M.13-17','M.18-24',
                            'M.25-34','M.35-44','M.45-54','M.55-64','M.65+'
                            ]
                        age_gender_data = [age_gender_dict[x] for x in age_gender_buckets]
                    except KeyError:
                        age_gender_data = ['' for x in range(21)]
                        print("no age or gender data for video %s" %video['id'])
                    videos_dict[video['id']] = age_gender_data + regions_data
            try: 
                videos = requests.get(videos['paging']['next']).json()
            except KeyError:
                pagination = False
            # end while

    print("Retrieved demographic data for %s videos" %str(len(videos_dict)))
    return videos_dict
