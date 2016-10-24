#!/usr/bin/python
# -*- coding: utf-8 -*-
from redshift import rsm
from fb import get_posts_and_interactions, get_total_reach, get_video_stats
from settings import aws_access_key, aws_secret_key, s3_bucket
import boto
import csv
import argparse

def create_import_file(interval=False, import_type='posts', filename='fb_import_posts.csv', list_id = None):
    if import_type == 'posts':
        import_file = open(filename, 'w')
        data_dict = get_total_reach(get_posts_and_interactions(interval))
    if import_type == 'videos':
        import_file = open(filename, 'w')
        data_dict = get_video_stats(interval)
    if import_type == 'video_lab_videos':
        import_file = open(filename, 'w')
        data_dict = get_video_stats(interval, True, list_id)
    csv_file = csv.writer(import_file, quoting=csv.QUOTE_MINIMAL)
    csv_file.writerows([[id,]+values for id, values in data_dict.items()])
    import_file.close()

def upload_to_s3(filename='fb_import_posts.csv'):
    conn = boto.connect_s3(aws_access_key, aws_secret_key)
    bucket = conn.lookup(s3_bucket)
    k = boto.s3.key.Key(bucket) 
    k.key = filename
    k.set_contents_from_filename(filename)

def update_redshift(table_name, columns, primary_key, filename):
    staging_table_name = table_name + "_staging"
    column_names = ", ".join(columns)
    columns_to_stage = ", ".join([(column + " = s." + column) for column in columns ])
    table_key = table_name + "." + primary_key
    staging_table_key = "s." + primary_key

    command = """-- Create a staging table 
CREATE TABLE %s (LIKE %s);

-- Load data into the staging table 
COPY %s (%s) 
FROM 's3://%s/%s' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
FILLRECORD
delimiter ','; 

-- Update records 
UPDATE %s
SET %s
FROM %s s
WHERE %s = %s; 

-- Insert records 
INSERT INTO %s 
SELECT s.* FROM %s s LEFT JOIN %s 
ON %s = %s
WHERE %s IS NULL;

-- Drop the staging table
DROP TABLE %s; 

-- End transaction 
END;"""%(staging_table_name, table_name, staging_table_name, column_names, s3_bucket, filename, aws_access_key, aws_secret_key, table_name, columns_to_stage, staging_table_name, table_key, staging_table_key, table_name, staging_table_name, table_name, staging_table_key, table_key, table_key, staging_table_name )

    rsm.db_query(command)
    return

posts = {}
posts['interval'] = 'month'
posts['import_type'] = 'posts'
posts['filename'] = 'fb_import_posts.csv'
posts['tablename'] = 'facebook.posts'
posts['columns'] = ['post_id', 'message', 'created_time', 'likes', 'shares', 'comments', 'total_reach']
posts['primary_key'] = 'post_id'

videos = {}
videos['interval'] = False
videos['import_type'] = 'videos'
videos['filename'] = 'fb_import_videos.csv'
videos['tablename'] = 'facebook.videos'
videos['columns'] = ['video_id', 'title', 'description', 'created_time', 'video_length', 'likes', 'comments', 'reactions', 'shares', 'reach', 'ms_viewed ', 'total_views', 'unique_viewers', 'views_10sec', 'views_30sec', 'views_95pct', 'avg_completion']
videos['primary_key'] = 'video_id'

video_lab_videos = {}
video_lab_videos['interval'] = False
video_lab_videos['import_type'] = 'video_lab_videos'
video_lab_videos['filename'] = 'fb_import_video_lab.csv'
video_lab_videos['tablename'] = 'facebook.video_lab_videos'
video_lab_videos['columns'] = ['video_id', 'title', 'description', 'created_time', 'video_length', 'likes', 'comments', 'reactions', 'shares', 'reach', 'ms_viewed ', 'total_views', 'unique_viewers', 'views_10sec', 'views_30sec', 'views_95pct', 'avg_sec_watched','avg_completion']
video_lab_videos['primary_key'] = 'video_id'
video_lab_videos['list_id'] = '1563848167245359'

video_lab_videos_2 = {}
video_lab_videos_2['interval'] = False
video_lab_videos_2['import_type'] = 'video_lab_videos'
video_lab_videos_2['filename'] = 'fb_import_video_lab_2.csv'
video_lab_videos_2['tablename'] = 'facebook.video_lab_videos'
video_lab_videos_2['columns'] = ['video_id', 'title', 'description', 'created_time', 'video_length', 'likes', 'comments', 'reactions', 'shares', 'reach', 'ms_viewed ', 'total_views', 'unique_viewers', 'views_10sec', 'views_30sec', 'views_95pct', 'avg_sec_watched', 'avg_completion']
video_lab_videos_2['primary_key'] = 'video_id'
video_lab_videos_2['list_id'] = '1225720367451359'

data_types = [posts, videos, video_lab_videos, video_lab_videos_2]

for item in data_types:
    if 'list_id' in item:
        create_import_file(item.get('interval'), item.get('import_type'), item.get('filename'), item.get('list_id'))
    else:
        create_import_file(item.get('interval'), item.get('import_type'), item.get('filename'))
    print("created " + item.get('filename')) 
    
    upload_to_s3(item.get('filename'))
    print("uploaded " + item.get('filename') + " to s3")
    
    update_redshift(item.get('tablename'), item.get('columns'), item.get('primary_key'), item.get('filename'))
    print("updated redshift table " + item.get('tablename'))