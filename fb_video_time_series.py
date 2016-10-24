""" Gets and imports the video time series data into redshift.
    Separate file so it can easily be scheduled separately from the other, bulkier facebook data imports.
"""

from redshift import rsm
from fb_tools import create_import_file, upload_to_s3
from settings import s3_bucket, aws_access_key, aws_secret_key
from time import gmtime, strftime

def update_redshift_video_time_series():
    command = """-- Create a staging table 
CREATE TABLE facebook.video_time_series_staging (LIKE facebook.video_time_series);

-- Load data into the staging table 
COPY facebook.video_time_series_staging (video_id, title, created_time, snapshot_time, total_views, unique_viewers, views_10sec) 
FROM 's3://%s/fb_video_time_series.csv' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
FILLRECORD
delimiter ','; 

-- Insert records 
INSERT INTO facebook.video_time_series
SELECT * FROM facebook.video_time_series_staging;

-- Drop the staging table
DROP TABLE facebook.video_time_series_staging; 

-- End transaction 
END;"""%(s3_bucket, aws_access_key, aws_secret_key)

    rsm.db_query(command)

print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
create_import_file(False, import_type='time_series', filename='fb_video_time_series.csv')
print("created fb_video_time_series.csv")
upload_to_s3("fb_video_time_series.csv")
print("uploaded fb_video_time_series.csv to s3")
update_redshift_video_time_series()
print("updated redshift table facebook.video_time_series")