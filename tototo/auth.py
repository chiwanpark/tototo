# -*- coding: utf-8 -*-
from functools import wraps
from flask import url_for, request, session
from tototo import db_session
from tototo.database import User
from werkzeug.utils import redirect


def signin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session['user_id'] is None:
            return redirect(url_for('users.get_signin', dest=request.url, message='로그인이 필요합니다.'))
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session['user_id'] != 1:
            return redirect(url_for('users.get_signin', dest=request.url, message='관리자만 접속할 수 있습니다.'))
        return f(*args, **kwargs)

    return decorated


def get_current_user() -> User:
    if 'user_id' not in session or session['user_id'] is None:
        return None

    return db_session.query(User).filter(User.id == session['user_id']).first()
