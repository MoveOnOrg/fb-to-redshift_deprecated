# Facebook to Redshift

Note: This uses Python3.


## Installation
1. Clone this repo
2. Create a virtualenv and activate it

  `virtualenv venv`
  
  `. venv/bin/activate`
3. Install requirements

  `pip install -r requirements.txt`

  * If you don't already have postgresql-devel installed, you'll need to run `yum install python-devel postgresql-devel` first or else you'll get an error like `pg_config executable not found` when pip tries to install psycopg2.
  
4. Create settings.py (using settings.py.example as a template). 

  * If you haven't already, you will need to [register a Facebook app](https://developers.facebook.com/docs/apps/register) and [associate it with the page](http://stackoverflow.com/questions/9265062/how-to-link-a-facebook-app-with-an-existing-fan-page) you're looking to pull data for. You will need to also be an administrator of the page for this to work.
  
    * To get your long access token, first go to [Facebook's Graph API Explorer](https://developers.facebook.com/tools/explorer) and make sure it is associated with your app (top right drop down).
    * Get your user access token, ensuring `manage_pages` and `read_insights` are both selected as permissions.
    * Add your user access token in as the value in the variable `user_access_token` in settings.py.
    * Add your app id and app secret in the client_id and client_secret variables in settings.py.
    * In your virtualenv, run `python fb_get_token.py`.
    * Add the output of the script to settings.py as your `fb_long_token`. This expires every 60 days.

  * To obtain a never-expiring access token for production after registering the app and associating it with the page:

    * Go to [Facebook's Graph API Explorer](https://developers.facebook.com/tools/explorer) and make sure it is associated with your app (top right drop down).
    * Under Get Token, choose Get User Access Token, ensuring `manage_pages` and `read_insights` are both selected as permissions.
    * Under Get Token > Page Access Tokens, chose MoveOn.org
    * Click the little blue i to the left of the Token and note the expiration time. Choose Open in Access Token Tool.
    * Click the blue Extend Access Token button at the bottom of the page. The Access Token toward the top of the page should change. 
    * Click the "Debug" button to the right. "Expires" should show "Never"
    * Paste this token into settings.py as the value for `fb_long_token` 

  * To find the Facebook video list id, visit https://developers.facebook.com/tools/explorer/145634995501895/?method=GET&path=moveon%2F%3Ffields%3Dvideo_lists&version=v2.7 while logged into Facebook with a valid page token.
    
  * You will also need to have [created a Redshift database](http://docs.aws.amazon.com/redshift/latest/dg/t_creating_database.html), and have your [AWS IAM credentials](https://aws.amazon.com/iam/). Make sure to create tables in the schema `facebook`, named `posts` and `videos` and `video_lab_videos`.
    
    `CREATE TABLE facebook.posts(post_id VARCHAR(256) PRIMARY KEY, message VARCHAR(max), created_time timestamp, likes INT, shares INT, comments INT, total_reach INT, link_clicks INT);`

    `CREATE TABLE facebook.videos(video_id VARCHAR(256) PRIMARY KEY, title VARCHAR(max), description VARCHAR(max), created_time timestamp, video_length DECIMAL (6,2), likes INT, comments INT, reactions INT, shares INT NULL, reach BIGINT NULL, ms_viewed BIGINT NULL, total_views INT NULL, unique_viewers INT NULL, views_10sec INT NULL, views_30sec INT NULL, views_95pct INT NULL, avg_sec_watched DECIMAL (6,2), avg_completion DECIMAL(4,3) NULL, views_autoplayed INT, views_clicked_to_play INT, views_organic INT, views_organic_unique INT, views_paid INT, views_paid_unique INT, views_sound_on INT, complete_views INT, complete_views_unique INT, complete_views_auto_played INT, complete_views_clicked_to_play INT, complete_views_organic INT, complete_views_organic_unique INT, complete_views_paid INT, complete_views_paid_unique INT, views_10s_auto_played INT, views_10s_clicked_to_play INT, views_10s_organic INT, views_10s_paid INT, views_10s_sound_on INT, avg_time_watched BIGINT, view_total_time_organic BIGINT, view_total_time_paid BIGINT, impressions BIGINT, impressions_paid_unique BIGINT, impressions_paid BIGINT, impressions_organic_unique BIGINT, impressions_organic BIGINT, impressions_viral_unique BIGINT, impressions_viral BIGINT, impressions_fan_unique BIGINT, impressions_fan BIGINT, impressions_fan_paid_unique BIGINT, impressions_fan_paid BIGINT;`

    `CREATE TABLE facebook.video_lab_videos(video_id VARCHAR(256) PRIMARY KEY, title VARCHAR(max), description VARCHAR(max), created_time timestamp, video_length DECIMAL (6,2), likes INT, comments INT, reactions INT, shares INT NULL, reach BIGINT NULL, ms_viewed BIGINT NULL, total_views INT NULL, unique_viewers INT NULL, views_10sec INT NULL, views_30sec INT NULL, views_95pct INT NULL, avg_sec_watched DECIMAL (6,2), avg_completion DECIMAL(4,3) NULL, views_autoplayed INT, views_clicked_to_play INT, views_organic INT, views_organic_unique INT, views_paid INT, views_paid_unique INT, views_sound_on INT, complete_views INT, complete_views_unique INT, complete_views_auto_played INT, complete_views_clicked_to_play INT, complete_views_organic INT, complete_views_organic_unique INT, complete_views_paid INT, complete_views_paid_unique INT, views_10s_auto_played INT, views_10s_clicked_to_play INT, views_10s_organic INT, views_10s_paid INT, views_10s_sound_on INT, avg_time_watched BIGINT, view_total_time_organic BIGINT, view_total_time_paid BIGINT, impressions BIGINT, impressions_paid_unique BIGINT, impressions_paid BIGINT, impressions_organic_unique BIGINT, impressions_organic BIGINT, impressions_viral_unique BIGINT, impressions_viral BIGINT, impressions_fan_unique BIGINT, impressions_fan BIGINT, impressions_fan_paid_unique BIGINT, impressions_fan_paid BIGINT;`

    `CREATE TABLE facebook.video_time_series(video_id VARCHAR(256), title VARCHAR(max), created_time timestamp, snapshot_time timestamp, total_views INT NULL, unique_viewers INT NULL, views_10sec INT NULL, primary key (video_id, snapshot_time));`

    `CREATE TABLE facebook.video_lab_views_demographics (video_id BIGINT, U13_17 BIGINT, U18_24 BIGINT, U25_34 BIGINT, U35_44 BIGINT, U45_54 BIGINT, U55_64 BIGINT, U65_over BIGINT, F13_17 BIGINT, F18_24 BIGINT, F25_34 BIGINT, F35_44 BIGINT, F45_54 BIGINT, F55_64 BIGINT, F65_over BIGINT, M13_17 BIGINT, M18_24 BIGINT, M25_34 BIGINT, M35_44 BIGINT, M45_54 BIGINT, M55_64 BIGINT, M65_over BIGINT, region_1_name VARCHAR, region_1_views BIGINT, region_2_name VARCHAR, region_2_views BIGINT, region_3_name VARCHAR, region_3_views BIGINT, region_4_name VARCHAR, region_4_views BIGINT, region_5_name VARCHAR, region_5_views BIGINT, region_6_name VARCHAR, region_6_views BIGINT, region_7_name VARCHAR, region_7_views BIGINT, region_8_name VARCHAR, region_8_views BIGINT, region_9_name VARCHAR, region_9_views BIGINT, region_10_name VARCHAR, region_10_views BIGINT, region_11_name VARCHAR, region_11_views BIGINT, region_12_name VARCHAR, region_12_views BIGINT, region_13_name VARCHAR, region_13_views BIGINT, region_14_name VARCHAR, region_14_views BIGINT, region_15_name VARCHAR, region_15_views BIGINT, region_16_name VARCHAR, region_16_views BIGINT, region_17_name VARCHAR, region_17_views BIGINT, region_18_name VARCHAR, region_18_views BIGINT, region_19_name VARCHAR, region_19_views BIGINT, region_20_name VARCHAR, region_20_views BIGINT, region_21_name VARCHAR, region_21_views BIGINT, region_22_name VARCHAR, region_22_views BIGINT, region_23_name VARCHAR, region_23_views BIGINT, region_24_name VARCHAR, region_24_views BIGINT, region_25_name VARCHAR, region_25_views BIGINT, region_26_name VARCHAR, region_26_views BIGINT, region_27_name VARCHAR, region_27_views BIGINT, region_28_name VARCHAR, region_28_views BIGINT, region_29_name VARCHAR, region_29_views BIGINT, region_30_name VARCHAR, region_30_views BIGINT, region_31_name VARCHAR, region_31_views BIGINT, region_32_name VARCHAR, region_32_views BIGINT, region_33_name VARCHAR, region_33_views BIGINT, region_34_name VARCHAR, region_34_views BIGINT, region_35_name VARCHAR, region_35_views BIGINT, region_36_name VARCHAR, region_36_views BIGINT, region_37_name VARCHAR, region_37_views BIGINT, region_38_name VARCHAR, region_38_views BIGINT, region_39_name VARCHAR, region_39_views BIGINT, region_40_name VARCHAR, region_40_views BIGINT, region_41_name VARCHAR, region_41_views BIGINT, region_42_name VARCHAR, region_42_views BIGINT, region_43_name VARCHAR, region_43_views BIGINT, region_44_name VARCHAR, region_44_views BIGINT, region_45_name VARCHAR, region_45_views BIGINT);`

    `CREATE TABLE facebook.video_views_demographics (video_id BIGINT, U13_17 BIGINT, U18_24 BIGINT, U25_34 BIGINT, U35_44 BIGINT, U45_54 BIGINT, U55_64 BIGINT, U65_over BIGINT, F13_17 BIGINT, F18_24 BIGINT, F25_34 BIGINT, F35_44 BIGINT, F45_54 BIGINT, F55_64 BIGINT, F65_over BIGINT, M13_17 BIGINT, M18_24 BIGINT, M25_34 BIGINT, M35_44 BIGINT, M45_54 BIGINT, M55_64 BIGINT, M65_over BIGINT, region_1_name VARCHAR, region_1_views BIGINT, region_2_name VARCHAR, region_2_views BIGINT, region_3_name VARCHAR, region_3_views BIGINT, region_4_name VARCHAR, region_4_views BIGINT, region_5_name VARCHAR, region_5_views BIGINT, region_6_name VARCHAR, region_6_views BIGINT, region_7_name VARCHAR, region_7_views BIGINT, region_8_name VARCHAR, region_8_views BIGINT, region_9_name VARCHAR, region_9_views BIGINT, region_10_name VARCHAR, region_10_views BIGINT, region_11_name VARCHAR, region_11_views BIGINT, region_12_name VARCHAR, region_12_views BIGINT, region_13_name VARCHAR, region_13_views BIGINT, region_14_name VARCHAR, region_14_views BIGINT, region_15_name VARCHAR, region_15_views BIGINT, region_16_name VARCHAR, region_16_views BIGINT, region_17_name VARCHAR, region_17_views BIGINT, region_18_name VARCHAR, region_18_views BIGINT, region_19_name VARCHAR, region_19_views BIGINT, region_20_name VARCHAR, region_20_views BIGINT, region_21_name VARCHAR, region_21_views BIGINT, region_22_name VARCHAR, region_22_views BIGINT, region_23_name VARCHAR, region_23_views BIGINT, region_24_name VARCHAR, region_24_views BIGINT, region_25_name VARCHAR, region_25_views BIGINT, region_26_name VARCHAR, region_26_views BIGINT, region_27_name VARCHAR, region_27_views BIGINT, region_28_name VARCHAR, region_28_views BIGINT, region_29_name VARCHAR, region_29_views BIGINT, region_30_name VARCHAR, region_30_views BIGINT, region_31_name VARCHAR, region_31_views BIGINT, region_32_name VARCHAR, region_32_views BIGINT, region_33_name VARCHAR, region_33_views BIGINT, region_34_name VARCHAR, region_34_views BIGINT, region_35_name VARCHAR, region_35_views BIGINT, region_36_name VARCHAR, region_36_views BIGINT, region_37_name VARCHAR, region_37_views BIGINT, region_38_name VARCHAR, region_38_views BIGINT, region_39_name VARCHAR, region_39_views BIGINT, region_40_name VARCHAR, region_40_views BIGINT, region_41_name VARCHAR, region_41_views BIGINT, region_42_name VARCHAR, region_42_views BIGINT, region_43_name VARCHAR, region_43_views BIGINT, region_44_name VARCHAR, region_44_views BIGINT, region_45_name VARCHAR, region_45_views BIGINT);`


  * You'll also need to have [created a bucket in s3](http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-create-bucket.html).

  * Note: the connection to S3 uses the boto library which has [excellent docs](https://boto3.readthedocs.io/en/latest/guide/migrations3.html#creating-the-connection).
  
5. Run the script! Note: This script can take a *long time* to run, due to pagination, if the page you're pulling posts from has a lot of posts.
  
  `python fb_to_redshift.py`

  * You can limit the timeframe from which a run of the script grabs posts by passing an argument (e.g. 'year', 'month', 'week') to the calls to create_import_file() at the bottom of `fb_to_redshift.py`.

6. Optional: Run the time series script `python fb_video_time_series.py`
