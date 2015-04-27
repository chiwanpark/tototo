# -*- coding: utf-8 -*-
import os
import pytz

DATABASE_URI = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
TIMEZONE = pytz.timezone('Asia/Seoul')
