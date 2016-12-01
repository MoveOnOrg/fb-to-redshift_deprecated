#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Loop through the data types and run the other functions to
    download, format, upload and import data for each data type.
"""

from fb_tools import create_import_file, upload_to_s3, update_redshift
from time import gmtime, strftime
from settings import test, files_dir, s3_bucket, data_types, redshift_import

def main():
    print()
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    for item in data_types:
        if test:
            item['tablename'] += '_test'
        if 'list_id' in item:
            create_import_file(
                item.get('interval'), item.get('import_type'),
                item.get('filename'), item.get('columns'), item.get('list_id'))
        else:
            create_import_file(
                item.get('interval'), item.get('import_type'),
                item.get('filename'), item.get('columns'))
        print("created %s " %(files_dir + item.get('filename')))
        if redshift_import:
            upload_to_s3(item.get('filename'))
            print(
                "uploaded %s to s3 bucket s3://%s" 
                %(files_dir + item.get('filename'), s3_bucket))
            update_redshift(
                item.get('tablename'), item.get('columns'), 
                item.get('primary_key'), item.get('filename'))
            print("updated redshift table " + item.get('tablename'))
    print("Done!")

if __name__=='__main__':
   main()
