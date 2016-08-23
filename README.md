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
    
  * You will also need to have [created a Redshift database](http://docs.aws.amazon.com/redshift/latest/dg/t_creating_database.html), and have your [AWS IAM credentials](https://aws.amazon.com/iam/). Make sure to create tables in the schema `facebook`, named `posts` and `videos`
    
    `CREATE TABLE facebook.posts(post_id VARCHAR(256) PRIMARY KEY, message VARCHAR(max), created_time timestamp, likes INT, shares INT, comments INT, total_reach INT);`

    `CREATE TABLE facebook.videos(video_id VARCHAR(256) PRIMARY KEY, title VARCHAR(max), description VARCHAR(max), created_time timestamp, video_length DECIMAL (6,2), likes INT, comments INT, reactions INT, shares INT NULL, reach BIGINT NULL, minutes_viewed BIGINT NULL, total_views INT NULL, unique_viewers INT NULL, views_10sec INT NULL, views_30sec INT NULL, views_95pct INT NULL, avg_completion DECIMAL(4,3) NULL);`

  * You'll also need to have [created a bucket in s3](http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-create-bucket.html).

  * Note: the connection to S3 uses the boto library which has [excellent docs](https://boto3.readthedocs.io/en/latest/guide/migrations3.html#creating-the-connection).
  
5. Run the script! Note: This script can take a *long time* to run, due to pagination, if the page you're pulling posts from has a lot of posts.
  
  `python fb_to_redshift.py`

  * You can limit the timeframe from which a run of the script grabs posts by passing an argument (e.g. 'year', 'month', 'week') to the call to create_import_file() at the bottom of `fb_to_redshift.py`.
