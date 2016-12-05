#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
import os
import sqlalchemy
import sqlalchemy.orm

class RedShiftMediator(object):

    def __init__(self, settings):
        if settings.db_host == 'host:port':
            raise Exception("settings.db_host must be properly configured")
        self.dbengine = sqlalchemy.create_engine(
            'postgresql+psycopg2://{user}:{passwd}@{host}/{db}'.format(
                host=settings.db_host,
                user=settings.db_user,
                passwd=settings.db_pwd,
                db=settings.db_name),
            execution_options={'autocommit': True,})
        self.dbsession = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(bind=self.dbengine),
            scopefunc=os.getpid)

    def db_query(self, query, opts={}):
        return self.dbsession.execute(query, opts)

    def db_close(self):
        self.dbsession.close()
