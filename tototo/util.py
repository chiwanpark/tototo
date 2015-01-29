# -*- coding: utf-8 -*-
from datetime import datetime
from tototo import config


def localtime_format(value: datetime, fmt: str):
    return value.astimezone(config.TIMEZONE).strftime(fmt)
