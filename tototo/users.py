# -*- coding: utf-8 -*-
import re
from flask import Blueprint, render_template, request, session, redirect, url_for
from tototo.database import db_session, User

context = Blueprint('users', __name__, url_prefix='/users')

EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')


@context.route('/signin')
def get_signin():
    dest = request.args.get('dest', None)
    return render_template('signin.html', dest=dest)


@context.route('/signin', methods=('POST', ))
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
        dest = url_for('index')
    return redirect(dest)


@context.route('/signout')
def get_signout():
    if 'user_id' in session:
        del session['user_id']

    return redirect(url_for('index'))


@context.route('/signup')
def get_signup():
    return render_template('signup.html')


@context.route('/signup', methods=('POST', ))
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
