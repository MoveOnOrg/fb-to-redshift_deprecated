#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Runs all the things. Most of the functions that do the work live elsewhere. 
"""

from fb_tools import create_import_file, upload_to_s3, update_redshift
from time import gmtime, strftime
from settings import test, files_dir, s3_bucket, s3_bucket_dir

def main():
    posts = {}
    posts['interval'] = 'month'
    posts['import_type'] = 'posts'
    posts['filename'] = 'fb_import_posts.csv'
    posts['tablename'] = 'facebook.posts'
    posts['columns'] = [
        'post_id', 'message', 'created_time', 'likes',
        'shares','comments', 'total_reach', 'link_clicks'
        ]
    posts['primary_key'] = 'post_id'

    videos = {}
    videos['interval'] = False
    videos['import_type'] = 'videos'
    videos['filename'] = 'fb_import_videos.csv'
    videos['tablename'] = 'facebook.videos'
    videos['columns'] = ['video_id', 'title', 'description',
        'created_time', 'video_length', 'likes', 'comments', 'reactions',
        'shares', 'reach', 'ms_viewed ', 'total_views', 'unique_viewers',
        'views_10sec', 'views_30sec', 'views_95pct', 'avg_sec_watched',
        'avg_completion', 'views_autoplayed', 'views_clicked_to_play',
        'views_organic', 'views_organic_unique', 'views_paid',
        'views_paid_unique', 'views_sound_on', 'complete_views',
        'complete_views_unique', 'complete_views_auto_played',
        'complete_views_clicked_to_play', 'complete_views_organic',
        'complete_views_organic_unique', 'complete_views_paid',
        'complete_views_paid_unique', 'views_10s_auto_played',
        'views_10s_clicked_to_play', 'views_10s_organic', 'views_10s_paid',
        'views_10s_sound_on', 'avg_time_watched', 'view_total_time_organic',
        'view_total_time_paid', 'impressions', 'impressions_paid_unique',
        'impressions_paid', 'impressions_organic_unique', 'impressions_organic',
        'impressions_viral_unique', 'impressions_viral', 'impressions_fan_unique',
        'impressions_fan', 'impressions_fan_paid_unique', 'impressions_fan_paid'
        ]
    videos['primary_key'] = 'video_id'

    video_lab_videos = {}
    video_lab_videos['interval'] = False
    video_lab_videos['import_type'] = 'video_lab_videos'
    video_lab_videos['filename'] = 'fb_import_video_lab.csv'
    video_lab_videos['tablename'] = 'facebook.video_lab_videos'
    video_lab_videos['columns'] = ['video_id', 'title', 'description',
        'created_time', 'video_length', 'likes', 'comments', 'reactions',
        'shares', 'reach', 'ms_viewed ', 'total_views', 'unique_viewers',
        'views_10sec', 'views_30sec', 'views_95pct', 'avg_sec_watched',
        'avg_completion', 'views_autoplayed', 'views_clicked_to_play',
        'views_organic', 'views_organic_unique', 'views_paid',
        'views_paid_unique', 'views_sound_on', 'complete_views',
        'complete_views_unique', 'complete_views_auto_played',
        'complete_views_clicked_to_play', 'complete_views_organic',
        'complete_views_organic_unique', 'complete_views_paid',
        'complete_views_paid_unique', 'views_10s_auto_played',
        'views_10s_clicked_to_play', 'views_10s_organic', 'views_10s_paid',
        'views_10s_sound_on', 'avg_time_watched', 'view_total_time_organic',
        'view_total_time_paid', 'impressions', 'impressions_paid_unique',
        'impressions_paid', 'impressions_organic_unique', 'impressions_organic',
        'impressions_viral_unique', 'impressions_viral', 'impressions_fan_unique',
        'impressions_fan', 'impressions_fan_paid_unique', 'impressions_fan_paid'
        ]
    video_lab_videos['primary_key'] = 'video_id'
    video_lab_videos['list_id'] = '1563848167245359'

    video_lab_videos_2 = {}
    video_lab_videos_2['interval'] = False
    video_lab_videos_2['import_type'] = 'video_lab_videos'
    video_lab_videos_2['filename'] = 'fb_import_video_lab_2.csv'
    video_lab_videos_2['tablename'] = 'facebook.video_lab_videos'
    video_lab_videos_2['columns'] = ['video_id', 'title', 'description',
        'created_time', 'video_length', 'likes', 'comments', 'reactions',
        'shares', 'reach', 'ms_viewed ', 'total_views', 'unique_viewers',
        'views_10sec', 'views_30sec', 'views_95pct', 'avg_sec_watched',
        'avg_completion', 'views_autoplayed', 'views_clicked_to_play',
        'views_organic', 'views_organic_unique', 'views_paid',
        'views_paid_unique', 'views_sound_on', 'complete_views',
        'complete_views_unique', 'complete_views_auto_played',
        'complete_views_clicked_to_play', 'complete_views_organic',
        'complete_views_organic_unique', 'complete_views_paid',
        'complete_views_paid_unique', 'views_10s_auto_played',
        'views_10s_clicked_to_play', 'views_10s_organic', 'views_10s_paid',
        'views_10s_sound_on', 'avg_time_watched', 'view_total_time_organic',
        'view_total_time_paid', 'impressions', 'impressions_paid_unique',
        'impressions_paid', 'impressions_organic_unique', 'impressions_organic',
        'impressions_viral_unique', 'impressions_viral', 'impressions_fan_unique',
        'impressions_fan', 'impressions_fan_paid_unique', 'impressions_fan_paid'
        ]
    video_lab_videos_2['primary_key'] = 'video_id'
    video_lab_videos_2['list_id'] = '1225720367451359'

    video_demographics = {}
    video_demographics['interval'] = False
    video_demographics['import_type'] = 'views_demographics'
    video_demographics['filename'] = 'fb_video_views_demographics.csv'
    video_demographics['tablename'] = 'facebook.video_views_demographics'
    video_demographics['columns'] = ['video_id', 'U13_17', 'U18_24', 'U25_34',
        'U35_44', 'U45_54', 'U55_64', 'U65_over', 'F13_17', 'F18_24', 'F25_34',
        'F35_44', 'F45_54', 'F55_64', 'F65_over', 'M13_17', 'M18_24', 'M25_34',
        'M35_44', 'M45_54', 'M55_64', 'M65_over', 'region_1_name', 'region_1_views',
        'region_2_name', 'region_2_views', 'region_3_name', 'region_3_views',
        'region_4_name', 'region_4_views', 'region_5_name', 'region_5_views',
        'region_6_name', 'region_6_views', 'region_7_name', 'region_7_views',
        'region_8_name', 'region_8_views', 'region_9_name', 'region_9_views',
        'region_10_name', 'region_10_views', 'region_11_name', 'region_11_views',
        'region_12_name', 'region_12_views', 'region_13_name', 'region_13_views',
        'region_14_name', 'region_14_views', 'region_15_name', 'region_15_views',
        'region_16_name', 'region_16_views', 'region_17_name', 'region_17_views',
        'region_18_name', 'region_18_views', 'region_19_name', 'region_19_views',
        'region_20_name', 'region_20_views', 'region_21_name', 'region_21_views',
        'region_22_name', 'region_22_views', 'region_23_name', 'region_23_views',
        'region_24_name', 'region_24_views', 'region_25_name', 'region_25_views',
        'region_26_name', 'region_26_views', 'region_27_name', 'region_27_views',
        'region_28_name', 'region_28_views', 'region_29_name', 'region_29_views',
        'region_30_name', 'region_30_views', 'region_31_name', 'region_31_views',
        'region_32_name', 'region_32_views', 'region_33_name', 'region_33_views',
        'region_34_name', 'region_34_views', 'region_35_name', 'region_35_views',
        'region_36_name', 'region_36_views', 'region_37_name', 'region_37_views',
        'region_38_name', 'region_38_views', 'region_39_name', 'region_39_views',
        'region_40_name', 'region_40_views', 'region_41_name', 'region_41_views',
        'region_42_name', 'region_42_views', 'region_43_name', 'region_43_views',
        'region_44_name', 'region_44_views', 'region_45_name', 'region_45_views'
        ]
    video_demographics['primary_key'] = 'video_id'

    video_lab_demographics = {}
    video_lab_demographics['interval'] = False
    video_lab_demographics['import_type'] = 'views_demographics_video_lab'
    video_lab_demographics['filename'] = 'fb_video_lab_views_demographics.csv'
    video_lab_demographics['tablename'] = 'facebook.video_lab_views_demographics'
    video_lab_demographics['columns'] = ['video_id', 'U13_17', 'U18_24', 'U25_34',
        'U35_44', 'U45_54', 'U55_64', 'U65_over', 'F13_17', 'F18_24', 'F25_34',
        'F35_44', 'F45_54', 'F55_64', 'F65_over', 'M13_17', 'M18_24', 'M25_34',
        'M35_44', 'M45_54', 'M55_64', 'M65_over', 'region_1_name', 'region_1_views',
        'region_2_name', 'region_2_views', 'region_3_name', 'region_3_views',
        'region_4_name', 'region_4_views', 'region_5_name', 'region_5_views',
        'region_6_name', 'region_6_views', 'region_7_name', 'region_7_views',
        'region_8_name', 'region_8_views', 'region_9_name', 'region_9_views',
        'region_10_name', 'region_10_views', 'region_11_name', 'region_11_views',
        'region_12_name', 'region_12_views', 'region_13_name', 'region_13_views',
        'region_14_name', 'region_14_views', 'region_15_name', 'region_15_views',
        'region_16_name', 'region_16_views', 'region_17_name', 'region_17_views',
        'region_18_name', 'region_18_views', 'region_19_name', 'region_19_views',
        'region_20_name', 'region_20_views', 'region_21_name', 'region_21_views',
        'region_22_name', 'region_22_views', 'region_23_name', 'region_23_views',
        'region_24_name', 'region_24_views', 'region_25_name', 'region_25_views',
        'region_26_name', 'region_26_views', 'region_27_name', 'region_27_views',
        'region_28_name', 'region_28_views', 'region_29_name', 'region_29_views',
        'region_30_name', 'region_30_views', 'region_31_name', 'region_31_views',
        'region_32_name', 'region_32_views', 'region_33_name', 'region_33_views',
        'region_34_name', 'region_34_views', 'region_35_name', 'region_35_views',
        'region_36_name', 'region_36_views', 'region_37_name', 'region_37_views',
        'region_38_name', 'region_38_views', 'region_39_name', 'region_39_views',
        'region_40_name', 'region_40_views', 'region_41_name', 'region_41_views',
        'region_42_name', 'region_42_views', 'region_43_name', 'region_43_views',
        'region_44_name', 'region_44_views', 'region_45_name', 'region_45_views'
        ]
    video_lab_demographics['primary_key'] = 'video_id'
    video_lab_demographics['list_id'] = '1225720367451359'

    video_lab_demographics_2 = {}
    video_lab_demographics_2['interval'] = False
    video_lab_demographics_2['import_type'] = 'views_demographics_video_lab'
    video_lab_demographics_2['filename'] = 'fb_video_lab_views_demographics_2.csv'
    video_lab_demographics_2['tablename'] = 'facebook.video_lab_views_demographics'
    video_lab_demographics_2['columns'] = ['video_id', 'U13_17', 'U18_24', 'U25_34',
        'U35_44', 'U45_54', 'U55_64', 'U65_over', 'F13_17', 'F18_24', 'F25_34',
        'F35_44', 'F45_54', 'F55_64', 'F65_over', 'M13_17', 'M18_24', 'M25_34',
        'M35_44', 'M45_54', 'M55_64', 'M65_over', 'region_1_name', 'region_1_views',
        'region_2_name', 'region_2_views', 'region_3_name', 'region_3_views',
        'region_4_name', 'region_4_views', 'region_5_name', 'region_5_views',
        'region_6_name', 'region_6_views', 'region_7_name', 'region_7_views',
        'region_8_name', 'region_8_views', 'region_9_name', 'region_9_views',
        'region_10_name', 'region_10_views', 'region_11_name', 'region_11_views',
        'region_12_name', 'region_12_views', 'region_13_name', 'region_13_views',
        'region_14_name', 'region_14_views', 'region_15_name', 'region_15_views',
        'region_16_name', 'region_16_views', 'region_17_name', 'region_17_views',
        'region_18_name', 'region_18_views', 'region_19_name', 'region_19_views',
        'region_20_name', 'region_20_views', 'region_21_name', 'region_21_views',
        'region_22_name', 'region_22_views', 'region_23_name', 'region_23_views',
        'region_24_name', 'region_24_views', 'region_25_name', 'region_25_views',
        'region_26_name', 'region_26_views', 'region_27_name', 'region_27_views',
        'region_28_name', 'region_28_views', 'region_29_name', 'region_29_views',
        'region_30_name', 'region_30_views', 'region_31_name', 'region_31_views',
        'region_32_name', 'region_32_views', 'region_33_name', 'region_33_views',
        'region_34_name', 'region_34_views', 'region_35_name', 'region_35_views',
        'region_36_name', 'region_36_views', 'region_37_name', 'region_37_views',
        'region_38_name', 'region_38_views', 'region_39_name', 'region_39_views',
        'region_40_name', 'region_40_views', 'region_41_name', 'region_41_views',
        'region_42_name', 'region_42_views', 'region_43_name', 'region_43_views',
        'region_44_name', 'region_44_views', 'region_45_name', 'region_45_views'
        ]
    video_lab_demographics_2['primary_key'] = 'video_id'
    video_lab_demographics_2['list_id'] = '1563848167245359'

    data_types = [posts, videos, video_lab_videos, video_lab_videos_2,
        video_demographics, video_lab_demographics, video_lab_demographics_2
        ]

    print()
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    for item in data_types:
        if test:
            item['tablename'] += '_test'
        if 'list_id' in item:
            create_import_file(item.get('interval'), item.get('import_type'),
                item.get('filename'), item.get('list_id')
                )
        else:
            create_import_file(item.get('interval'), item.get('import_type'),
                item.get('filename')
                )
        print("created %s " %(files_dir + item.get('filename')))

        upload_to_s3(item.get('filename'))
        print("uploaded %s to s3 bucket s3://%s" %(files_dir + item.get('filename'), s3_bucket + '/' + s3_bucket_dir))
        
        update_redshift(item.get('tablename'), item.get('columns'), 
            item.get('primary_key'), item.get('filename'))
        print("updated redshift table " + item.get('tablename'))

if __name__=='__main__':
   main()
