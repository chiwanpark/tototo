# -*- coding: utf-8 -*-
import os
import pytz

DATABASE_URI = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
TIMEZONE = pytz.timezone('Asia/Seoul')
DATETIME_FORMAT = '%Y%m%d%H%M%S%z'
SENDGRID_API_USER = os.environ.get('SENDGRID_API_USER')
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
