#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Download data and create CSV. Upload CSV to S3. Import to Redshift.
"""

import sys
import os
local_settings_path = os.path.join(os.getcwd(),"settings.py")
if os.path.exists(local_settings_path):
    import imp
    settings = imp.load_source('settings', local_settings_path)

from redshift import RedShiftMediator
from fb import (
    get_posts_and_interactions, get_video_stats, get_video_time_series,
    get_video_views_demographics)
from settings import (
    aws_access_key, aws_secret_key, s3_bucket, s3_bucket_dir, files_dir, test)
import settings
import boto
import csv

rsm = None

def create_import_file(
        interval=False, import_type='posts',filename='fb_import_posts.csv',
        columns=False, list_id=None):
    import_file = open(files_dir + filename, 'w')
    if import_type == 'posts':
        data_dict = get_posts_and_interactions(interval)
    if import_type == 'videos':
        data_dict = get_video_stats(interval)
    if import_type == 'video_list':
        data_dict = get_video_stats(interval, list_id)
    if import_type == 'video_time_series':
        data_dict = get_video_time_series()
    if import_type == 'video_viewer_demographics':
        data_dict = get_video_views_demographics(interval)
    if import_type == 'video_list_viewer_demographics':
        data_dict = get_video_views_demographics(interval, list_id)
    if not data_dict:
        print("Could not retrieve %s data" %(import_type))
        return False
    csv_file = csv.writer(import_file, quoting=csv.QUOTE_MINIMAL)
    if columns:
        csv_file.writerow(columns)
    csv_file.writerows([[id,]+values for id, values in data_dict.items()])
    import_file.close()
    return True

def upload_to_s3(filename='fb_import_posts.csv'):
    conn = boto.connect_s3(aws_access_key, aws_secret_key)
    bucket = conn.lookup(s3_bucket)
    k = boto.s3.key.Key(bucket)
    k.key = '/' + s3_bucket_dir + '/' + filename
    k.set_contents_from_filename(files_dir + filename)

def update_redshift(table_name, columns, primary_key, filename):
    global rsm
    if rsm is None:
        rsm = RedShiftMediator(settings)
    staging_table_name = table_name + "_staging"
    column_names = ", ".join(columns)
    columns_to_stage = ", ".join([(column + " = s." + column) for column in columns])
    table_key = table_name + "." + primary_key
    staging_table_key = "s." + primary_key

    command = """-- Create a staging table 
CREATE TABLE %s (LIKE %s);

-- Load data into the staging table 
COPY %s (%s) 
FROM 's3://%s/%s/%s' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
FILLRECORD
delimiter ','
IGNOREHEADER 1; 

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
END;"""%(
    staging_table_name, table_name, staging_table_name, column_names,
    s3_bucket, s3_bucket_dir, filename, aws_access_key, aws_secret_key,
    table_name, columns_to_stage, staging_table_name, table_key,
    staging_table_key, table_name, staging_table_name, table_name,
    staging_table_key, table_key, table_key, staging_table_name)

    rsm.db_query(command)
