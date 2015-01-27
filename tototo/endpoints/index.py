# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from flask import Blueprint, render_template
from tototo import db_session
from tototo.auth import get_current_user
from tototo.database import Meeting

context = Blueprint('index', __name__)

@context.route('/')
def get_index():
    meeting_count = db_session.query(Meeting).filter(Meeting.when < datetime.now(tz=timezone.utc)).count()
    return render_template('index.html', meeting_count=meeting_count, current_user=get_current_user())
