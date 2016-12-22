#!/usr/bin/env python
from setuptools import find_packages, setup
import textwrap

setup(
    name='fb-to-redshift',
    version='0.1.2',
    author='Sandra Chung,Rivkah Standig',
    author_email='opensource@moveon.org',
    packages=['fb-to-redshift'],
    scripts=['fb-to-redshift/fb_get_token.py','fb-to-redshift/fb_to_redshift.py','fb-to-redshift/fb_video_time_series.py','fb-to-redshift/fb.py','fb-to-redshift/redshift.py'],
    url='https://github.com/MoveOnOrg/fb-to-redshift',
    license='MIT',
    description="Download Facebook Page post and video data in CSV format, and import into Amazon Redshift tables.",
    long_description=textwrap.dedent(open('README.md', 'r').read()),
    keywords = "python facebook redshift",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP'
    ],
)