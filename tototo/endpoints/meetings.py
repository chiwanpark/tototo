# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import desc
from tototo import config
from tototo.auth import signin_required, admin_required, get_current_user
from tototo.database import Registration, db_session, Meeting


context = Blueprint('meetings', __name__, url_prefix='/meetings')


@context.route('/')
@signin_required
def get_meetings():
    meetings = db_session.query(Meeting).order_by(desc(Meeting.registered)).all()
    return render_template('meetings-list.html', meetings=meetings, current_user=get_current_user())


@context.route('/<int:meeting_id>')
@signin_required
def get_meeting(meeting_id):
    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    return render_template('meeting.html', meeting=meeting, current_user=get_current_user())


@context.route('/add')
@admin_required
def get_form_meeting():
    return render_template('add-meeting.html', current_user=get_current_user())


@context.route('/', methods=('POST', ))
@admin_required
def post_meeting():
    name = request.form.get('name', None)
    where = request.form.get('where', None)
    when = request.form.get('when', None)
    available = request.form.get('available', 'off') == 'on'
    quota = int(request.form.get('quota', '-1'))

    if not name or not where or not when or quota == -1:
        return '', 400

    when = config.TIMEZONE.localize(datetime.strptime(when, '%Y-%m-%d %H:%M'))

    meeting = Meeting(name=name, where=where, when=when, available=available, quota=quota)
    db_session.add(meeting)
    db_session.commit()

    return redirect(url_for('meetings.get_meetings'))


@context.route('/registration/<int:meeting_id>')
@signin_required
def get_form_registration(meeting_id):
    message = request.args.get('message', None)
    current_user = get_current_user()
    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    registration = db_session.query(Registration).filter(Registration.user == current_user, Registration.meeting == meeting).first()

    if (not meeting or len(meeting.users) >= meeting.quota or not meeting.available) and not registration:
        return render_template('meeting.html', message='이미 끝난 모임이거나, 정원이 다 차버린 모임입니다.', meeting=meeting,
                               current_user=get_current_user())

    return render_template('registration.html', participant=current_user, current_user=current_user, next_meeting=meeting,
                           message=message, registration=registration)


@context.route('/registration', methods=('POST', ))
@signin_required
def post_registration():
    participant = get_current_user()
    memo = request.form.get('memo', None)
    meeting_id = int(request.form.get('meeting_id', '-1'))

    if not memo:
        return redirect(url_for('meetings.get_form_registration', meeting_id=meeting_id, message='모임에서 달성할 목표는 반드시 입력해야합니다.'))

    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        return redirect(url_for('meetings.get_form_registration', meeting_id=meeting_id, message='해당 모임이 존재하지 않습니다.'))

    registration = db_session.query(Registration).filter(Registration.user == participant, Registration.meeting == meeting).first()
    if not registration:
        if not meeting.available or len(meeting.users) >= meeting.quota:
            return redirect(url_for('meetings.get_form_registration', meeting_id=meeting_id, message='해당 모임에는 참가할 수 없습니다.'))
        registration = Registration(user_id=participant.id, meeting_id=meeting_id)

    registration.memo = memo
    db_session.add(registration)
    db_session.commit()

    return redirect(url_for('meetings.get_meeting', meeting_id=meeting_id))
