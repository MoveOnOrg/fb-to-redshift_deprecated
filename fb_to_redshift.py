#!/usr/bin/python
# -*- coding: utf-8 -*-
from redshift import rsm
from fb import get_posts_and_interactions, get_total_reach, get_video_stats
from settings import aws_access_key, aws_secret_key, s3_bucket
import boto
import csv
import argparse

def create_import_file(interval=False, import_type='posts'):
    if import_type == 'posts':
        import_file = open('fb_import_posts.csv', 'w')
        data_dict = get_total_reach(get_posts_and_interactions(interval))
    if import_type == 'videos':
        import_file = open('fb_import_videos.csv', 'w')
        data_dict = get_video_stats(interval)
    if import_type == 'video_lab':
        import_file = open('fb_import_video_lab.csv', 'w')
        data_dict = get_video_stats(interval,True)
    csv_file = csv.writer(import_file, quoting=csv.QUOTE_MINIMAL)
    csv_file.writerows([[id,]+values for id, values in data_dict.items()])
    import_file.close()

def upload_to_s3(filename='fb_import_posts.csv'):
    conn = boto.connect_s3(aws_access_key, aws_secret_key)
    bucket = conn.lookup(s3_bucket)
    k = boto.s3.key.Key(bucket) 
    k.key = filename
    k.set_contents_from_filename(filename)

def update_redshift_posts():
    command = """-- Create a staging table 
CREATE TABLE facebook.posts_staging (LIKE facebook.posts);

-- Load data into the staging table 
COPY facebook.posts_staging (post_id, message, created_time, likes, shares, comments, total_reach) 
FROM 's3://%s/fb_import_posts.csv' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
delimiter ','; 

-- Update records 
UPDATE facebook.posts
SET message = s.message, created_time = s.created_time, likes = s.likes, shares = s.shares, comments = s.comments, total_reach = s.total_reach
FROM facebook.posts_staging s 
WHERE facebook.posts.post_id = s.post_id; 

-- Insert records 
INSERT INTO facebook.posts
SELECT s.* FROM facebook.posts_staging s LEFT JOIN facebook.posts
ON s.post_id = facebook.posts.post_id
WHERE facebook.posts.post_id IS NULL;

-- Drop the staging table
DROP TABLE facebook.posts_staging; 

-- End transaction 
END;"""%(s3_bucket, aws_access_key, aws_secret_key)

    rsm.db_query(command)

def update_redshift_videos():
    command = """-- Create a staging table 
CREATE TABLE facebook.videos_staging (LIKE facebook.videos);

-- Load data into the staging table 
COPY facebook.videos_staging (video_id, title, description, created_time, video_length, likes, comments, reactions, shares, reach, ms_viewed, total_views, unique_viewers, views_10sec, views_30sec, views_95pct, avg_completion) 
FROM 's3://%s/fb_import_videos.csv' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
FILLRECORD
delimiter ','; 

-- Update records 
UPDATE facebook.videos 
SET title = s.title, description = s.description, created_time = s.created_time, video_length = s.video_length, likes = s.likes, comments = s.comments, reactions = s.reactions, shares = s.shares, reach = s.reach, ms_viewed = s.ms_viewed, total_views = s.total_views, unique_viewers = s.unique_viewers, views_10sec = s.views_10sec, views_30sec = s.views_30sec, views_95pct = s.views_95pct, avg_completion = s.avg_completion
FROM facebook.videos_staging s
WHERE facebook.videos.video_id = s.video_id; 

-- Insert records 
INSERT INTO facebook.videos 
SELECT s.* FROM facebook.videos_staging s LEFT JOIN facebook.videos 
ON s.video_id = facebook.videos.video_id
WHERE facebook.videos.video_id IS NULL;

-- Drop the staging table
DROP TABLE facebook.videos_staging; 

-- End transaction 
END;"""%(s3_bucket, aws_access_key, aws_secret_key)

    rsm.db_query(command)

def update_redshift_video_lab_videos():
    command = """-- Create a staging table 
CREATE TABLE facebook.video_lab_staging (LIKE facebook.video_lab_videos);

-- Load data into the staging table 
COPY facebook.video_lab_staging (video_id, title, description, created_time, video_length, likes, comments, reactions, shares, reach, ms_viewed, total_views, unique_viewers, views_10sec, views_30sec, views_95pct, avg_completion) 
FROM 's3://%s/fb_import_video_lab.csv' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
FILLRECORD
delimiter ','; 

-- Update records 
UPDATE facebook.video_lab_videos 
SET title = s.title, description = s.description, created_time = s.created_time, video_length = s.video_length, likes = s.likes, comments = s.comments, reactions = s.reactions, shares = s.shares, reach = s.reach, ms_viewed = s.ms_viewed, total_views = s.total_views, unique_viewers = s.unique_viewers, views_10sec = s.views_10sec, views_30sec = s.views_30sec, views_95pct = s.views_95pct, avg_completion = s.avg_completion
FROM facebook.video_lab_staging s
WHERE facebook.video_lab_videos.video_id = s.video_id; 

-- Insert records 
INSERT INTO facebook.video_lab_videos 
SELECT s.* FROM facebook.video_lab_staging s LEFT JOIN facebook.video_lab_videos 
ON s.video_id = facebook.video_lab_videos.video_id
WHERE facebook.video_lab_videos.video_id IS NULL;

-- Drop the staging table
DROP TABLE facebook.video_lab_staging; 

-- End transaction 
END;"""%(s3_bucket, aws_access_key, aws_secret_key)

    rsm.db_query(command)

create_import_file('month', 'posts')
create_import_file(False, 'videos')
create_import_file(False, 'video_lab')
upload_to_s3('fb_import_posts.csv')
upload_to_s3('fb_import_videos.csv')
upload_to_s3('fb_import_video_lab.csv')
update_redshift_posts()
update_redshift_videos()
update_redshift_video_lab_videos()