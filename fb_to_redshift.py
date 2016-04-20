#!/usr/bin/python
# -*- coding: utf-8 -*-
from redshift import rsm
from fb import get_posts, get_interactions
from settings import aws_access_key, aws_secret_key, s3_bucket
import boto

def create_import_file():
    import_file = open('fb_import_file.csv', 'w')
    fb_dict = get_interactions(get_posts())
    post_ids = fb_dict.keys()
    first_line = '%s,%s,%s,%s,%s,%s'%(post_ids[0], fb_dict[post_ids[0]][0], fb_dict[post_ids[0]][1], fb_dict[post_ids[0]][2], fb_dict[post_ids[0]][3], fb_dict[post_ids[0]][4])
    import_file.write(first_line)
    for post_id in post_ids[1:]:
        line = '\n%s,%s,%s,%s,%s,%s'%(post_id, fb_dict[post_id][0], fb_dict[post_id][1], fb_dict[post_id][2], fb_dict[post_id][3], fb_dict[post_id][4])
        import_file.write(line)
    import_file.close()

def upload_to_s3():
    conn = boto.connect_s3(aws_access_key, aws_secret_key)
    bucket = conn.lookup(s3_bucket)
    k = boto.s3.key.Key(bucket) 
    k.key = 'fb_import_file.csv'
    k.set_contents_from_filename('fb_import_file.csv') 

def update_redshift():
    command = """-- Create a staging table 
CREATE TABLE facebook.posts_staging (LIKE facebook.posts);

-- Load data into the staging table 
COPY facebook.posts_staging (post_id, message, created_time, likes, shares, comments) 
FROM 's3://%s/fb_import_file.csv' 
CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
delimiter ','; 

-- Update records 
UPDATE facebook.posts 
SET message = s.message, created_time = s.created_time, likes = s.likes, shares = s.shares, comments = s.comments
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

create_import_file()
upload_to_s3()
update_redshift()
