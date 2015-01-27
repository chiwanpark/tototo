# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from tototo.auth import signin_required, admin_required, get_current_user
from tototo.database import Registration, db_session, Meeting

context = Blueprint('meetings', __name__, url_prefix='/meetings')


@context.route('/')
@signin_required
def get_meetings():
    meetings = db_session.query(Meeting).all()
    return render_template('meetings-list.html', meetings=meetings)


@context.route('/<int:meeting_id>')
@signin_required
def get_meeting(meeting_id):
    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    return render_template('meeting.html', meeting=meeting)


@context.route('/add')
@admin_required
def get_form_meeting():
    return render_template('add-meeting.html')


@context.route('/', methods=('POST', ))
@admin_required
def post_meeting():
    name = request.form.get('name', None)
    location = request.form.get('location', None)
    when = request.form.get('when', None)
    available = request.form.get('available', 'off') == 'on'
    quota = int(request.form.get('quota', '-1'))

    if not name or not location or not when or quota == -1:
        return '', 400

    when = datetime.strptime(when, '%Y-%m-%d %H:%M')

    meeting = Meeting(name=name, location=location, when=when, available=available, quota=quota)
    db_session.add(meeting)
    db_session.commit()

    return redirect(url_for('meetings.get_meetings'))


@context.route('/registration')
@signin_required
def get_form_registration():
    message = request.args.get('message', None)
    current_user = get_current_user()
    next_meeting = db_session.query(Meeting).filter(Meeting.available).first()
    registration = db_session.query(Registration).filter(Registration.user == current_user, Registration.meeting == next_meeting).first()

    return render_template(
        'registration.html', participant=current_user, next_meeting=next_meeting, message=message, registration=registration)


@context.route('/registration', methods=('POST', ))
@signin_required
def post_registration():
    participant = get_current_user()
    memo = request.form.get('memo', None)
    meeting_id = int(request.form.get('meeting_id', '-1'))

    if not memo:
        return redirect(url_for('meetings.get_form_registration', message='모임에서 달성할 목표는 반드시 입력해야합니다.'))

    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting or not meeting.available or len(meeting.users) >= meeting.quota:
        return redirect(url_for('meetings.get_form_registration', message='해당 모임에는 참가할 수 없습니다.'))

    registration = db_session.query(Registration).filter(Registration.user == participant, Registration.meeting == meeting).first()
    if not registration:
        registration = Registration(user_id=participant.id, meeting_id=meeting_id)

    registration.memo = memo
    db_session.add(registration)
    db_session.commit()

    return redirect(url_for('meetings.get_meetings'))
