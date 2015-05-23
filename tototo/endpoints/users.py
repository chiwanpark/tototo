# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import re
from flask import Blueprint, render_template, request, session, redirect, url_for
from tototo import config
from tototo.auth import get_current_user
from tototo.database import db_session, User
from tototo.notification import send_email_to_user
from tototo.crypto import valid_token, create_token

context = Blueprint('users', __name__, url_prefix='/users')

EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')


@context.route('/signin')
def get_signin():
    message = request.args.get('message', None)
    dest = request.args.get('dest', None)
    return render_template('signin.html', dest=dest, message=message, current_user=get_current_user())


@context.route('/signin', methods=('POST',))
def post_signin():
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    dest = request.args.get('dest', None)

    user = db_session.query(User).filter(User.email == email, User.password == password).first()
    if user:
        session['user_id'] = user.id
    else:
        return render_template('signin.html', message='로그인 정보가 잘못되었습니다.')

    if not dest:
        dest = url_for('index.get_index')
    return redirect(dest)


@context.route('/signout')
def get_signout():
    if 'user_id' in session:
        del session['user_id']

    return redirect(url_for('index.get_index'))


@context.route('/signup')
def get_signup():
    return render_template('signup.html')


@context.route('/signup', methods=('POST',))
def post_signup():
    email = request.form.get('email', None)
    name = request.form.get('name', None)
    password = request.form.get('password', None)
    password_confirm = request.form.get('password_confirm', None)
    mail_subscribe = request.form.get('mail_subscribe', 'off') == 'on'

    message = None

    # validation of user input
    if not EMAIL_REGEX.match(email):
        message = '이메일 형식이 올바르지 않습니다.'
    elif password != password_confirm:
        message = '입력한 두 비밀번호가 서로 다릅니다.'
    elif not name:
        message = '이름이 입력되지 않았습니다.'

    # check user duplication
    if db_session.query(User).filter(User.email == email).count() > 0:
        message = '동일한 이메일 주소로 가입된 사용자가 존재합니다.'

    if message:
        return render_template('signup.html', message=message, input_email=email, input_name=name)

    # add user
    user = User(name=name, email=email, password=password, mail_subscribe=mail_subscribe)
    db_session.add(user)
    db_session.commit()

    return render_template('signup-success.html')


@context.route('/find-password')
def get_find_password():
    return render_template('find-password.html')


@context.route('/find-password', methods=('POST',))
def post_find_password():
    email = request.form.get('email', '')

    if not email:
        return render_template('find-password.html', message='메일 주소를 입력해주세요.')

    user = db_session.query(User).filter(User.email == email).first()
    if not user:
        return render_template('find-password.html', message='해당 메일 주소를 갖는 사용자가 없습니다.')

    expired = datetime.now(tz=config.TIMEZONE) + timedelta(minutes=30)
    args = {
        'config': config,
        'expired': expired,
        'email': email,
        'user_id': user.id,
        'token': create_token(email, 'form_change_password', expired)
    }
    if send_email_to_user(user, '[tototo] 요청하신 비밀번호 찾기 메일입니다.', 'mail-find-password.html', args):
        return render_template('find-password-send-complete.html')

    return render_template('error.html', message='비밀번호 찾기 메일 발송에 실패했습니다.')


@context.route('/<int:user_id>/change-password')
def get_change_password(user_id: int):
    token = request.args.get('token', '')
    email = request.args.get('email', '')
    expired = request.args.get('expired', '')

    now = datetime.now(tz=config.TIMEZONE)
    expired = datetime.strptime(expired, config.DATETIME_FORMAT)
    if expired < now or not valid_token(token, email, 'form_change_password', expired):  # fail
        return render_template('error.html', message='잘못된 비밀번호 변경 요청입니다.')

    new_expired = now + timedelta(minutes=30)
    new_token = create_token(str(user_id), 'post_change_password', new_expired)
    return render_template('change-password.html', config=config, email=email, user_id=user_id, token=new_token,
                           expired=new_expired)


@context.route('/<int:user_id>/change-password', methods=('POST',))
def post_change_password(user_id: int):
    email = request.form.get('email', '')
    token = request.form.get('token', '')
    expired = request.form.get('expired', '')
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')

    now = datetime.now(tz=config.TIMEZONE)
    expired = datetime.strptime(expired, config.DATETIME_FORMAT)
    if expired < now or not valid_token(token, str(user_id), 'post_change_password', expired):  # fail
        return render_template('error.html', message='잘못된 비밀번호 변경 요청입니다.')

    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        return render_template('error.html', message='해당 사용자 정보가 존재하지 않습니다.')

    if password != password_confirm:
        return render_template('change-password.html', message='비밀번호와 비밀번호 확인이 일치하지 않습니다.', config=config,
                               email=email, token=token, expired=expired, user_id=user_id)

    user.password = password
    db_session.add(user)
    db_session.commit()

    return render_template('change-password-success.html')
