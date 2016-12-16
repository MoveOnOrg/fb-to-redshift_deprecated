# Facebook to Redshift

This project connects to the Facebook Graph API (v2.7), downloads the latest data about posts and videos associated with a target Page, and formats and outputs the data as CSVs. It also (optionally) uploads the CSVs into an Amazon S3 bucket and imports the data into a corresponding table into Redshift using the `copy` command.

Many, many settings in this script must/can be customized to suit your needs.

## Requirements

* Python3
* Facebook account with admin access to target Facebook Page
* (optional) Amazon S3 bucket and Redshift user with ability to create tables in a given schema (named `facebook` in the examples here)

## Installation and use

### 1. Clone this repo
### 2. Create a virtualenv and activate it. 

If Python 3 is not your default Python version, you'll need to tell virtualenv which version of Python to use.

  `virtualenv venv` or `virtualenv -p /path/to/python3 venv`

  `. venv/bin/activate`

### 3. Install requirements

  `pip install -r requirements.txt`

  * If you don't already have postgresql-devel installed, you'll need to run `yum install python-devel postgresql-devel` first or else you'll get an error like `pg_config executable not found` when pip tries to install psycopg2.
  
### 4. Create settings.py (using settings.py.example as a template). 

  * If you haven't already, you will need to [register a Facebook app](https://developers.facebook.com/docs/apps/register) and [associate it with the Page](http://stackoverflow.com/questions/9265062/how-to-link-a-facebook-app-with-an-existing-fan-page) you're looking to pull data for. You will need to also be an administrator of the Page for this to work.
  
#### a. Get a long-lived access token (`fb_long_token`)
  * Go to [Facebook's Graph API Explorer](https://developers.facebook.com/tools/explorer) and make sure it is associated with your app (top right drop down).
  * Get your user access token, ensuring `manage_pages` and `read_insights` are both selected as permissions.
  * Add your user access token in as the value in the variable `user_access_token` in settings.py.
  * Add your app id and app secret in the client_id and client_secret variables in settings.py.
  * In your virtualenv, run `python fb_get_token.py`.
  * Add the output of the script to settings.py as your `fb_long_token`. This expires every 60 days.

  * To obtain a never-expiring access token for production after registering the app and associating it with the page:
    * Go to [Facebook's Graph API Explorer](https://developers.facebook.com/tools/explorer) and make sure it is associated with your app (top right drop down).
    * Under Get Token, choose Get User Access Token, ensuring `manage_pages` and `read_insights` are both selected as permissions.
    * Under Get Token > Page Access Tokens, chose your target Page.
    * Click the little blue i to the left of the Token and note the expiration time. Choose Open in Access Token Tool.
    * Click the blue Extend Access Token button at the bottom of the page. The Access Token toward the top of the page should change. 
    * Click the "Debug" button to the right. "Expires" should show "Never"
    * Paste this token into settings.py as the value for `fb_long_token` 

#### b. Create or copy a parameter dictionary for each data CSV, using examples in settings.py. Add each dictionary to the list of `data_types` in settings.py.

  * If you run fb_to_redshift.py now with `redshift_import` set to False and without editing the parameter dictionaries, and your Page has post and video data, you should find three tidy CSVs (fb_posts.csv, fb_videos.csv and fb_video_viewer_demographics.csv) in the directory you specified in the `files_dir` variable -- assuming you got the Facebook settings right.

  * There are six types of data downloads available, with corresponding template dictionaries in settings.py and retrieval functions in fb.py: 
    * Basic post data (`posts` via `get_posts_and_interactions`)
    * Video insights for all Page videos OR for all Page videos in a video list (`videos` and `video_list` via `get_video_stats`)
    * Video viewer demographics for all Page videos OR for all Page videos in a video list (`video_viewer_demographics` and `video_list_viewer_demographics` via `get_video_views_demographics`)
    * Simple video view stats, collected at regular intervals to create a time series of video views (See fb_video_time_series.py and `get_video_time_series`)

  * If you want to use `video_list` or `video_list_viewer_demographics` to pull video data from only the videos in a particular Facebook Page list, you'll need to get the list_ids.
    * To find the Facebook video list ids, visit [Graph API explorer](https://developers.facebook.com/tools/explorer/) and get a valid Page token. Next to `GET -> /v2.8/` enter `[page_id]?fields=video_lists` and submit to get a list of all the Page video lists and IDs.
  * `['interval']` can be used in combination with `post_limit` to limit the amount of data retrieved by each API call. If you leave `['interval']` set to `False` the script will try to pull all available post or video data.
  * `['tablename']` is used only if `redshift_import` is set to True.
  * **!IMPORTANT**: `data_types` should include only the parameter dictionaries that correspond to CSVs that you want to generate (and maybe import). The script will loop through them to get the corresponding data.
    
#### c. (OPTIONAL) Set up Redshift import.
  * Set `redshift_import` to True, and this script will attempt to upload the generated CSVs to an S3 bucket and import the data into Redshift tables.
  * If you don't already have one, [create a bucket in S3](http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-create-bucket.html) and add its unique name to `s3_bucket` in settings.py.
  * [Create a Redshift database](http://docs.aws.amazon.com/redshift/latest/dg/t_creating_database.html), and get your [AWS IAM credentials](https://aws.amazon.com/iam/). Add database connection info and IAM credentials to settings.py.
  * Create tables in the schema `facebook` that correspond to the tablename and columns defined in your parameter dictionaries. The Redshift user whose credentials are in settings.py should own those tables and have the ability to add tables to that schema.Example table creation queries below match the example dictionaries:
    
    `CREATE TABLE facebook.posts(post_id VARCHAR(256) PRIMARY KEY, message VARCHAR(max), created_time timestamp, likes INT, shares INT, comments INT, total_reach INT, link_clicks INT);`

    `CREATE TABLE facebook.videos(video_id VARCHAR(256) PRIMARY KEY, title VARCHAR(max), description VARCHAR(max), created_time timestamp, video_length DECIMAL (6,2), likes INT, comments INT, reactions INT, shares INT NULL, reach BIGINT NULL, ms_viewed BIGINT NULL, total_views INT NULL, unique_viewers INT NULL, views_10sec INT NULL, views_30sec INT NULL, views_95pct INT NULL, avg_sec_watched DECIMAL (6,2), avg_completion DECIMAL(4,3) NULL, page_owned_views INT, shared_views INT, views_autoplayed INT, views_clicked_to_play INT, views_organic INT, views_organic_unique INT, views_paid INT, views_paid_unique INT, views_sound_on INT, complete_views INT, complete_views_unique INT, complete_views_auto_played INT, complete_views_clicked_to_play INT, complete_views_organic INT, complete_views_organic_unique INT, complete_views_paid INT, complete_views_paid_unique INT, views_10s_auto_played INT, views_10s_clicked_to_play INT, views_10s_organic INT, views_10s_paid INT, views_10s_sound_on INT, avg_time_watched BIGINT, view_total_time_organic BIGINT, view_total_time_paid BIGINT, impressions BIGINT, impressions_paid_unique BIGINT, impressions_paid BIGINT, impressions_organic_unique BIGINT, impressions_organic BIGINT, impressions_viral_unique BIGINT, impressions_viral BIGINT, impressions_fan_unique BIGINT, impressions_fan BIGINT, impressions_fan_paid_unique BIGINT, impressions_fan_paid BIGINT;`

    `CREATE TABLE facebook.video_viewer_demographics (video_id BIGINT, U13_17 BIGINT, U18_24 BIGINT, U25_34 BIGINT, U35_44 BIGINT, U45_54 BIGINT, U55_64 BIGINT, U65_over BIGINT, F13_17 BIGINT, F18_24 BIGINT, F25_34 BIGINT, F35_44 BIGINT, F45_54 BIGINT, F55_64 BIGINT, F65_over BIGINT, M13_17 BIGINT, M18_24 BIGINT, M25_34 BIGINT, M35_44 BIGINT, M45_54 BIGINT, M55_64 BIGINT, M65_over BIGINT, region_1_name VARCHAR, region_1_views BIGINT, region_2_name VARCHAR, region_2_views BIGINT, region_3_name VARCHAR, region_3_views BIGINT, region_4_name VARCHAR, region_4_views BIGINT, region_5_name VARCHAR, region_5_views BIGINT, region_6_name VARCHAR, region_6_views BIGINT, region_7_name VARCHAR, region_7_views BIGINT, region_8_name VARCHAR, region_8_views BIGINT, region_9_name VARCHAR, region_9_views BIGINT, region_10_name VARCHAR, region_10_views BIGINT, region_11_name VARCHAR, region_11_views BIGINT, region_12_name VARCHAR, region_12_views BIGINT, region_13_name VARCHAR, region_13_views BIGINT, region_14_name VARCHAR, region_14_views BIGINT, region_15_name VARCHAR, region_15_views BIGINT, region_16_name VARCHAR, region_16_views BIGINT, region_17_name VARCHAR, region_17_views BIGINT, region_18_name VARCHAR, region_18_views BIGINT, region_19_name VARCHAR, region_19_views BIGINT, region_20_name VARCHAR, region_20_views BIGINT, region_21_name VARCHAR, region_21_views BIGINT, region_22_name VARCHAR, region_22_views BIGINT, region_23_name VARCHAR, region_23_views BIGINT, region_24_name VARCHAR, region_24_views BIGINT, region_25_name VARCHAR, region_25_views BIGINT, region_26_name VARCHAR, region_26_views BIGINT, region_27_name VARCHAR, region_27_views BIGINT, region_28_name VARCHAR, region_28_views BIGINT, region_29_name VARCHAR, region_29_views BIGINT, region_30_name VARCHAR, region_30_views BIGINT, region_31_name VARCHAR, region_31_views BIGINT, region_32_name VARCHAR, region_32_views BIGINT, region_33_name VARCHAR, region_33_views BIGINT, region_34_name VARCHAR, region_34_views BIGINT, region_35_name VARCHAR, region_35_views BIGINT, region_36_name VARCHAR, region_36_views BIGINT, region_37_name VARCHAR, region_37_views BIGINT, region_38_name VARCHAR, region_38_views BIGINT, region_39_name VARCHAR, region_39_views BIGINT, region_40_name VARCHAR, region_40_views BIGINT, region_41_name VARCHAR, region_41_views BIGINT, region_42_name VARCHAR, region_42_views BIGINT, region_43_name VARCHAR, region_43_views BIGINT, region_44_name VARCHAR, region_44_views BIGINT, region_45_name VARCHAR, region_45_views BIGINT);`

    `CREATE TABLE facebook.video_list(video_id VARCHAR(256) PRIMARY KEY, title VARCHAR(max), description VARCHAR(max), created_time timestamp, video_length DECIMAL (6,2), likes INT, comments INT, reactions INT, shares INT NULL, reach BIGINT NULL, ms_viewed BIGINT NULL, total_views INT NULL, unique_viewers INT NULL, views_10sec INT NULL, views_30sec INT NULL, views_95pct INT NULL, avg_sec_watched DECIMAL (6,2), avg_completion DECIMAL(4,3) NULL, page_owned_views INT, shared_views INT, views_autoplayed INT, views_clicked_to_play INT, views_organic INT, views_organic_unique INT, views_paid INT, views_paid_unique INT, views_sound_on INT, complete_views INT, complete_views_unique INT, complete_views_auto_played INT, complete_views_clicked_to_play INT, complete_views_organic INT, complete_views_organic_unique INT, complete_views_paid INT, complete_views_paid_unique INT, views_10s_auto_played INT, views_10s_clicked_to_play INT, views_10s_organic INT, views_10s_paid INT, views_10s_sound_on INT, avg_time_watched BIGINT, view_total_time_organic BIGINT, view_total_time_paid BIGINT, impressions BIGINT, impressions_paid_unique BIGINT, impressions_paid BIGINT, impressions_organic_unique BIGINT, impressions_organic BIGINT, impressions_viral_unique BIGINT, impressions_viral BIGINT, impressions_fan_unique BIGINT, impressions_fan BIGINT, impressions_fan_paid_unique BIGINT, impressions_fan_paid BIGINT;`

    `CREATE TABLE facebook.video_list_viewer_demographics (video_id BIGINT, U13_17 BIGINT, U18_24 BIGINT, U25_34 BIGINT, U35_44 BIGINT, U45_54 BIGINT, U55_64 BIGINT, U65_over BIGINT, F13_17 BIGINT, F18_24 BIGINT, F25_34 BIGINT, F35_44 BIGINT, F45_54 BIGINT, F55_64 BIGINT, F65_over BIGINT, M13_17 BIGINT, M18_24 BIGINT, M25_34 BIGINT, M35_44 BIGINT, M45_54 BIGINT, M55_64 BIGINT, M65_over BIGINT, region_1_name VARCHAR, region_1_views BIGINT, region_2_name VARCHAR, region_2_views BIGINT, region_3_name VARCHAR, region_3_views BIGINT, region_4_name VARCHAR, region_4_views BIGINT, region_5_name VARCHAR, region_5_views BIGINT, region_6_name VARCHAR, region_6_views BIGINT, region_7_name VARCHAR, region_7_views BIGINT, region_8_name VARCHAR, region_8_views BIGINT, region_9_name VARCHAR, region_9_views BIGINT, region_10_name VARCHAR, region_10_views BIGINT, region_11_name VARCHAR, region_11_views BIGINT, region_12_name VARCHAR, region_12_views BIGINT, region_13_name VARCHAR, region_13_views BIGINT, region_14_name VARCHAR, region_14_views BIGINT, region_15_name VARCHAR, region_15_views BIGINT, region_16_name VARCHAR, region_16_views BIGINT, region_17_name VARCHAR, region_17_views BIGINT, region_18_name VARCHAR, region_18_views BIGINT, region_19_name VARCHAR, region_19_views BIGINT, region_20_name VARCHAR, region_20_views BIGINT, region_21_name VARCHAR, region_21_views BIGINT, region_22_name VARCHAR, region_22_views BIGINT, region_23_name VARCHAR, region_23_views BIGINT, region_24_name VARCHAR, region_24_views BIGINT, region_25_name VARCHAR, region_25_views BIGINT, region_26_name VARCHAR, region_26_views BIGINT, region_27_name VARCHAR, region_27_views BIGINT, region_28_name VARCHAR, region_28_views BIGINT, region_29_name VARCHAR, region_29_views BIGINT, region_30_name VARCHAR, region_30_views BIGINT, region_31_name VARCHAR, region_31_views BIGINT, region_32_name VARCHAR, region_32_views BIGINT, region_33_name VARCHAR, region_33_views BIGINT, region_34_name VARCHAR, region_34_views BIGINT, region_35_name VARCHAR, region_35_views BIGINT, region_36_name VARCHAR, region_36_views BIGINT, region_37_name VARCHAR, region_37_views BIGINT, region_38_name VARCHAR, region_38_views BIGINT, region_39_name VARCHAR, region_39_views BIGINT, region_40_name VARCHAR, region_40_views BIGINT, region_41_name VARCHAR, region_41_views BIGINT, region_42_name VARCHAR, region_42_views BIGINT, region_43_name VARCHAR, region_43_views BIGINT, region_44_name VARCHAR, region_44_views BIGINT, region_45_name VARCHAR, region_45_views BIGINT);`
  
### 5. Run the script!

  `python fb_to_redshift.py`

  * This script can take a *long time* to run, due to pagination, if the Page you're pulling from has a lot of posts or videos.

  * You'll get an error if you try to pull too much data at once. Edit `post_limit` and the `[interval]` parameter to reduce the amount of data you're requesting per API call.

  * If you set `test` to `True`, your CSVs will have '_test' appended to the filename. If you also set `redshift_import` to 'true', the script will append '_test' to the tablenames - so you must create tables in advance of running the script in test mode for import to work. E.g. `CREATE TABLE facebook.videos_test (LIKE facebook.videos)`.

### 6. Optional: Generate a time series of video views. 

  `python fb_video_time_series.py`

  * fb_to_redshift.py grabs the latest data for posts/videos created during the (optional) specified `['interval']`. fb_video_time_series.py grabs a specific set of data for videos created after the `time_series_start_date` in settings.py. If you set redshift_import to `True`, fb_to_redshift.py will overwrite the latest data for existing videos already in the table, while fb_video_time_series.py appends a new row for the latest video at the time of data capture (`snapshot_time`). Thus with the time series option running at regular intervals (e.g. on a cron job) you can capture the way video views, reactions, etc. change over time.
  * fb_video_time_series.py uses the same settings.py file as fb_to_redshift.py, and it's encapsulated in its own file so it's easy to run it independently from the rest of the code.
  * Create the Redshift table before running the time series code:

    `CREATE TABLE facebook.video_time_series(video_id VARCHAR(256), title VARCHAR(max), created_time timestamp, snapshot_time timestamp, total_views INT NULL, unique_viewers INT NULL, views_10sec INT NULL, reach BIGINT NULL, ms_viewed BIGINT NULL, likes INT NULL, comments INT NULL, reactions INT NULL, shares INT NULL, primary key (video_id, snapshot_time));`

## FAQ

####1. How do I get different data from the Graph API?

  * Changing which fields are retrieved requires editing the parameter dictionaries and the corresponding functions in fb.py. If you're importing data into Redshift as well, you'll need to change the column names and data types to match. This is fussy work! Refer to the [Graph API reference](https://developers.facebook.com/docs/graph-api/reference) to guide you through which fields you need and use the [Graph API explorer](https://developers.facebook.com/tools/explorer/) to test and tweak your new URL and generate a sample API response.

####2. I want to rename/reorder the columns in the CSVs.

  * You can edit the column names in the ['columns'] parameter in the appropriate parameter dictionary; but keep in mind that if you want to reorder the columns you'll also have to change the order in the appropriate fb.py function. Changing column order will also break Redshift import unless you also rename the Redshift table columns.

## Ideas for potential contributions

* Integration with the Facebook Marketing API for ads data.
* Data import into other database types.
* Other tools that facilitate download, formatting and import of data from Facebook.
