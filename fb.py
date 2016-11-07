#!/usr/bin/python
# -*- coding: utf-8 -*-
""" All the functions that work with the Graph API to get data.
"""

from settings import fb_version, fb_page_id, fb_long_token, post_limit, time_series_start_date
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

# this fn results in posts_dict = {post_id: [message, created_time, likes, shares, comments]}
# set interval = False to update all post data

def get_posts_and_interactions(interval=False):
    
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

    while too_many_posts_at_a_time:
        if interval:
            url = (base_url +
                '%s/posts?fields=message,created_time,id,\
                likes.limit(0).summary(total_count),\
                comments.limit(0).summary(total_count),\
                shares,\
                insights.metric(post_impressions){values,name}\
                &limit=%s&since=%s&until=%s&access_token=%s' %(fb_page_id,
                    limit, since, now, fb_long_token)
                )
        else:
            url = (base_url +
                '%s/posts?fields=message,created_time,id,\
                likes.limit(0).summary(true),\
                comments.limit(0).summary(true),\
                shares,\
                insights.metric(post_impressions){values,name}\
                &limit=%s&access_token=%s' %(fb_page_id, limit, fb_long_token)
                )
        
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
            insights = {}
            no_insights = False
            try:
                insights_data = post['insights']['data']
            except KeyError:
                no_insights = True
            for insight in insights_data:
                insights[insight['name']] = insight['values'][0]['value']
            if no_insights:
                posts_dict[post['id']] = [
                    message,
                    created_time,
                    likes,
                    shares,
                    comments
                    ]
            else:
                try:
                    impressions = insights['post_impressions']
                except KeyError:
                    impressions = 0
                finally:
                    posts_dict[post['id']] = [
                        message,
                        created_time,
                        likes,
                        shares,
                        comments,
                        impressions
                        ]
            
        if 'paging' in posts:
            posts = requests.get(posts['paging']['next']).json()
        else:
            pagination = False

    print("Retrieved data for %s posts" %str(len(posts_dict)))
    return posts_dict

def get_video_stats(interval = False, video_lab = False, list_id = None):
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

    while too_many_videos_at_a_time:

        if video_lab:
            if interval:
                url = (base_url +
                    '%s/?fields=videos{title,description,created_time,length,\
                    likes.limit(0).summary(total_count),\
                    comments.limit(0).summary(total_count),\
                    reactions.limit(0).summary(total_count),\
                    video_insights}&limit=%s&since=%s&until=%s\
                    &access_token=%s' %(list_id, limit, since, now, fb_long_token)
                    )
            else:
                url = (base_url +
                    '%s/?fields=videos{title,description,created_time,length,\
                    likes.limit(0).summary(total_count),\
                    comments.limit(0).summary(total_count),\
                    reactions.limit(0).summary(total_count),\
                    video_insights}&limit=%s&access_token=%s' %(list_id, limit, fb_long_token)
                    )
        else:
            if interval:
                url = (base_url + 
                    '%s/videos?fields=title,description,created_time,length,\
                    comments.limit(0).summary(total_count),\
                    likes.limit(0).summary(total_count),\
                    reactions.limit(0).summary(total_count),\
                    video_insights{values,name}&limit=%s&since=%s&until=%s\
                    &access_token=%s' %(fb_page_id, limit, since, now, fb_long_token)
                    )
            else:
                url = (base_url +
                    '%s/videos?fields=title,description,created_time,length,\
                    comments.limit(0).summary(total_count),\
                    likes.limit(0).summary(total_count),\
                    shares.limit(0).summary(total_count),\
                    reactions.limit(0).summary(total_count),\
                    video_insights{values,name}&limit=%s&access_token=%s' %(fb_page_id,
                        limit, fb_long_token)
                    )

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
                avg_sec_watched = round(float(insights['total_video_avg_time_watched']) / 1000.0, 3)
                avg_completion = round(float(insights['total_video_avg_time_watched']) / length / 1000.0, 3)
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
                    insights['total_video_impressions_fan_paid'] 
                    ]
        try: 
            videos = requests.get(videos['paging']['next']).json()
        except KeyError:
            pagination = False
        # end while

    print("Retrieved data for %s videos" %str(len(videos_dict)))
    return videos_dict

def get_video_time_series(start_date = time_series_start_date):
    
    since = int(datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp())
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    too_many_videos_at_a_time = True

    limit = post_limit

    while too_many_videos_at_a_time:
        url = (base_url +
            '%s/videos?fields=title,created_time,video_insights{values,name}\
            &limit=%s&since=%s&access_token=%s' %(fb_page_id, limit, since, 
                fb_long_token)
            )

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
                videos_dict[video['id']] = [
                    title, created_time, now,
                    insights['total_video_views'],
                    insights['total_video_views_unique'],
                    insights['total_video_10s_views_unique']]
        try: 
            videos = requests.get(videos['paging']['next']).json()
        except KeyError:
            pagination = False
        # end while

    return videos_dict

def get_video_view_demographics(interval = False, video_lab = False, list_id = None):
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

    while too_many_videos_at_a_time:

        if video_lab:
            if interval:
                url = (base_url +
                    '%s/?fields=videos{video_insights.metric(total_video_view_time_by_region_id,\
                    total_video_view_time_by_age_bucket_and_gender)}\
                    &limit=%s&since=%s&until=%s&access_token=%s' %(list_id,
                        limit, since, now, fb_long_token)
                    )
            else:
                url = (base_url +
                    '%s/?fields=videos{video_insights.metric(total_video_view_time_by_region_id,\
                    total_video_view_time_by_age_bucket_and_gender)}\
                    &limit=%s&access_token=%s' %(list_id, limit, fb_long_token)
                    )
        else:
            if interval:
                url = (base_url + 
                    '%s/videos?fields=video_insights.metric(total_video_view_time_by_region_id,\
                    total_video_view_time_by_age_bucket_and_gender){values,name}\
                    &limit=%s&since=%s&until=%s&access_token=%s' %(fb_page_id,
                        limit, since, now, fb_long_token)
                    )
            else:
                url = (base_url +
                    '%s/videos?fields=video_insights.metric(total_video_view_time_by_region_id,\
                    total_video_view_time_by_age_bucket_and_gender){values,name}\
                    &limit=%s&access_token=%s' %(fb_page_id, limit, fb_long_token)
                    )

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
            insights = {}
            no_insights = False
            try:
                insights_data = video['video_insights']['data']
            except KeyError:
                no_insights = True
            for insight in insights_data:
                insights[insight['name']] = insight['values'][0]['value']
            if no_insights:
                videos_dict[video['id']] = []
            else:
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
