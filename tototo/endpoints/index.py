# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, render_template
from sqlalchemy import desc
from tototo import db_session, config
from tototo.auth import get_current_user
from tototo.database import Meeting


context = Blueprint('index', __name__)


@context.route('/')
def get_index():
    meeting_count = db_session.query(Meeting).filter(Meeting.when < datetime.now(tz=config.TIMEZONE)).count()
    next_meeting = db_session.query(Meeting).filter(Meeting.available).order_by(desc(Meeting.registered)).first()
    return render_template('index.html', meeting_count=meeting_count, current_user=get_current_user(), next_meeting=next_meeting)
