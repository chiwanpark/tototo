# -*- coding: utf-8 -*-
from datetime import datetime
import re

from jinja2 import evalcontextfilter, escape, Markup
from tototo import config, app
from tototo.database import datetime_now


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
_image_re = re.compile(r'\[image\|http(?P<src>.*?)\]')


@app.template_filter()
def localtime_format(value: datetime, fmt: str):
    return value.astimezone(tz=config.TIMEZONE).strftime(fmt)


@app.template_filter()
@evalcontextfilter
def html_filter(ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))
    result = _image_re.sub('<img class="user-image" src="http\g<src>"/>', result)
    if ctx.autoescape:
        result = Markup(result)
    return result


@app.template_filter()
def dday(value: datetime):
    now = datetime_now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=config.TIMEZONE)
    return (now - value.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=config.TIMEZONE)).days
