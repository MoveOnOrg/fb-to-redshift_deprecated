# Facebook to Redshift

Note: This uses Python3

## Installation
1. Clone this repo
2. Create a virtualenv and activate it

  `virtualenv venv`
  
  `. venv/bin/activate`
3. Install requirements

  `pip install -r requirements.txt`
  
4. Create settings.py (using settings.py.example as a template). 

  a. If you haven't already, you will need to [register a Facebook app](https://developers.facebook.com/docs/apps/register).
  
  b. You will also need to have [created a Redshift database](http://docs.aws.amazon.com/redshift/latest/dg/t_creating_database.html), and have your [AWS IAM credentials](https://aws.amazon.com/iam/). Make sure to create a table in the schema `facebook`, named `posts`. 
    
    `CREATE TABLE facebook.posts(post_id VARCHAR(256) PRIMARY KEY, message VARCHAR(max), created_time timestamp, likes INT, shares INT, comments INT);`
    
  c. You'll also need to have [created a bucket in s3](http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-create-bucket.html).
  
5. Run the script!
  
  `python fb_to_redshift.py`
