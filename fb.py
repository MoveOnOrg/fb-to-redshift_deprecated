#!/usr/bin/python
# -*- coding: utf-8 -*-
from settings import fb_version, fb_page_id, fb_long_token, post_limit
import requests
import json
import sys
import time
import datetime

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

# this results in videos_dict = {video_id: [title, description, created_time, length, likes, comments, reactions, total_video_view_total_time, total_video_views_unique, total_video_10s_views_unique, total_video_30s_views_unique, total_video_avg_time_watched, total_video_impressions_unique, shares]}

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
    too_many_videos_at_a_time = True

    while too_many_videos_at_a_time:
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

    while pagination:
        for video in videos['data']:
            title = video.get('title', '').replace('\n', ' ').replace(',', ' ')
            description = video.get('description', '').replace('\n', ' ').replace(',', ' ')
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
            
            #parse insights
            insights = {}
            no_insights = False
            try:
                insights_data = video['video_insights']['data']
            except KeyError:
                no_insights = True
            for insight in insights_data:
                insights[insight['name']] = insight['values'][0]['value']
            
            try:
                shares = insights['total_video_stories_by_action_type']['share']
            except KeyError:
                shares = 0

            if no_insights:
                videos_dict[video['id']] = [title, description, created_time, length, likes, comments, reactions]
            else:
                videos_dict[video['id']] = [title, description, created_time, length, likes, comments, reactions, insights['total_video_view_total_time'], insights['total_video_views_unique'], insights['total_video_10s_views_unique'], insights['total_video_30s_views_unique'], insights['total_video_avg_time_watched'], insights['total_video_impressions_unique'], shares]
        try: 
            videos = requests.get(videos['paging']['next']).json()
        except KeyError:
            pagination = False
        # end while

    return videos_dict

#for dev only
#videos = get_video_stats()
#for video in videos:
#    print(video, videos[video])