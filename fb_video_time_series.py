#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Get and import video view data into Redshift. Run this regularly
    (perhaps on a cron job) to generate a time series of video views
    data in the specified Redshift table.
"""

from redshift import rsm
from fb_tools import create_import_file, upload_to_s3
from settings import s3_bucket, aws_access_key, aws_secret_key
from time import gmtime, strftime

columns = (
    'video_id,title,created_time,snapshot_time,total_views,'
    'unique_viewers,views_10sec')
tablename = 'facebook.video_time_series'
filename = 'fb_video_time_series.csv'

def update_redshift_video_time_series():
    command = """-- Create a staging table 
CREATE TABLE %s_staging (LIKE %s);

-- Load data into the staging table 
COPY %s_staging (%s) 
FROM 's3://%s/%s' 
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
    tablename, tablename, tablename, columns, s3_bucket, filename,
    aws_access_key, aws_secret_key, tablename, tablename, tablename)

    rsm.db_query(command)

def main():
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    create_import_file(
        False, import_type='time_series', filename='fb_video_time_series.csv',
        columns=columns)
    print("created %s" %filename)
    upload_to_s3(filename)
    print("uploaded %s to s3" %filename)
    update_redshift_video_time_series()
    print("updated redshift table %s" %tablename)

if __name__=='__main__':
   main()