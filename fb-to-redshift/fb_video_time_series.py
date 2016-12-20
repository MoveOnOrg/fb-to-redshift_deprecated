#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Get and import video view data into Redshift. Run this regularly
    (perhaps on a cron job) to generate a time series of video views
    data in the specified Redshift table.
"""

import sys
import os
local_settings_path = os.path.join(os.getcwd(),"settings.py")
if os.path.exists(local_settings_path):
    import imp
    settings = imp.load_source('settings', local_settings_path)

from redshift import RedShiftMediator
from fb_tools import create_import_file, upload_to_s3
from settings import (
    s3_bucket, s3_bucket_dir, aws_access_key, aws_secret_key, test,
    redshift_import)
import settings
from time import gmtime, strftime

columns = (
    'video_id,title,created_time,snapshot_time,likes,comments,reactions,total_views,'
    'unique_viewers,views_10sec,reach,ms_viewed,shares')
tablename = 'facebook.video_time_series'
filename = 'fb_video_time_series.csv'

if test:
    tablename += '_test'
    filename = ('_test.').join(filename.split('.'))

def update_redshift_video_time_series(rsm):
    command = """-- Create a staging table 
CREATE TABLE %s_staging (LIKE %s);

-- Load data into the staging table 
COPY %s_staging (%s) 
FROM 's3://%s/%s/%s' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
FILLRECORD
delimiter ','
IGNOREHEADER 1; 

-- Insert records 
INSERT INTO %s
SELECT * FROM %s_staging;

-- Drop the staging table
DROP TABLE %s_staging; 

-- End transaction 
END;"""%(
    tablename, tablename, tablename, columns, s3_bucket, s3_bucket_dir, filename,
    aws_access_key, aws_secret_key, tablename, tablename, tablename)

    rsm.db_query(command)

def main():
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    columns_list = columns.split(',')
    rsm = RedShiftMediator(settings)
    created_file = create_import_file(
        False, import_type='video_time_series', filename=filename, columns=columns_list)
    if created_file:
        print("created %s" %filename)
        if redshift_import:
            upload_to_s3(filename)
            print("uploaded %s to s3" %filename)
            update_redshift_video_time_series(rsm)
            print("updated redshift table %s" %tablename)

if __name__=='__main__':
   main()
