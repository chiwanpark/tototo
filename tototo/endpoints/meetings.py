# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import desc
from tototo import config
from tototo.auth import signin_required, admin_required, get_current_user
from tototo.database import Registration, db_session, Meeting, Slide

context = Blueprint('meetings', __name__, url_prefix='/meetings')


@context.route('/')
def get_meetings():
    meetings = db_session.query(Meeting).order_by(desc(Meeting.registered)).all()
    return render_template('meetings-list.html', meetings=meetings, current_user=get_current_user())


@context.route('/<int:meeting_id>')
def get_meeting(meeting_id):
    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    return render_template('meeting.html', meeting=meeting, current_user=get_current_user(), config=config)


@context.route('/<int:meeting_id>/modify')
@admin_required
def form_modify_meeting(meeting_id):
    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        return render_template('error.html', current_user=get_current_user(), message='해당 모임 정보가 없습니다.')
    return render_template('form-meeting.html', meeting=meeting, current_user=get_current_user(), config=config)


@context.route('/new')
@admin_required
def get_form_meeting():
    return render_template('form-meeting.html', current_user=get_current_user(), config=config)


def get_meeting_data_from_request():
    name = request.form.get('name', None)
    where = request.form.get('where', None)
    location_lat = float(request.form.get('location_lat', '0.0'))
    location_lng = float(request.form.get('location_lng', '0.0'))
    when = request.form.get('when', None)
    when_end = request.form.get('when_end', None)
    available = request.form.get('available', 'off') == 'on'
    quota = int(request.form.get('quota', '-1'))

    if not name or not where or not when or not when_end or quota == -1 or location_lat < 0.1 or location_lng < 0.1:
        raise ValueError()

    return name, where, location_lat, location_lng, when, when_end, available, quota


@context.route('/<int:meeting_id>/modify', methods=('POST',))
@admin_required
def modify_meeting(meeting_id):
    try:
        name, where, location_lat, location_lng, when, when_end, available, quota = get_meeting_data_from_request()
    except ValueError:
        return render_template('error.html', current_user=get_current_user(), message='잘못된 요청입니다.'), 400

    meeting = db_session.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        return render_template('error.html', current_user=get_current_user(), message='해당 모임 정보가 없습니다.')

    when = config.TIMEZONE.localize(datetime.strptime(when, '%Y-%m-%d %H:%M'))
    when_end = config.TIMEZONE.localize(datetime.strptime(when_end, '%Y-%m-%d %H:%M'))

    meeting.name = name
    meeting.where = where
    meeting.location_lat = location_lat
    meeting.location_lng = location_lng
    meeting.when = when
    meeting.when_end = when_end
    meeting.available = available
    meeting.quota = quota
    db_session.add(meeting)
    db_session.commit()

    return redirect(url_for('meetings.get_meetings'))


@context.route('/', methods=('POST', ))
@admin_required
def post_meeting():
    try:
        name, where, location_lat, location_lng, when, when_end, available, quota = get_meeting_data_from_request()
    except ValueError:
        return render_template('error.html', current_user=get_current_user(), message='잘못된 요청입니다.'), 400

    when = config.TIMEZONE.localize(datetime.strptime(when, '%Y-%m-%d %H:%M'))
    when_end = config.TIMEZONE.localize(datetime.strptime(when_end, '%Y-%m-%d %H:%M'))

    meeting = Meeting(
        name=name, where=where, when=when, when_end=when_end, available=available, quota=quota,
        location_lat=location_lat, location_lng=location_lng)
    db_session.add(meeting)
    db_session.commit()

    return redirect(url_for('meetings.get_meetings'))


@context.route('/<int:meeting_id>/registration')
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


@context.route('/<int:meeting_id>/registration', methods=('POST', ))
@signin_required
def post_registration(meeting_id):
    participant = get_current_user()
    memo = request.form.get('memo', None)

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


@context.route('/<int:meeting_id>/registration/<int:registration_id>/manage', methods=('POST',))
@admin_required
def manage_registration(meeting_id, registration_id):
    registration = db_session.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        return render_template('error.html', message='해당 참가 신청이 존재하지 않습니다.')
    if meeting_id != registration.meeting_id:
        return render_template('error.html', message='해당 참가 신청 데이터가 잘못되었습니다. (not matched meeting id)')
    status = request.form.get('status', None)
    if status not in ['waiting', 'accepted', 'cancelled', 'refused', 'not-attended']:
        return render_template('error.html', message='참가 신청 상태 정보가 잘못되었습니다. (' + str(status) + ')')

    registration.status = status
    db_session.add(registration)
    db_session.commit()

    return redirect(url_for('meetings.get_meeting', meeting_id=meeting_id))


@context.route('/<int:meeting_id>/slides')
@admin_required
def form_post_slide(meeting_id):
    return render_template('form-slides.html', meeting_id=meeting_id, current_user=get_current_user())


@context.route('/<int:meeting_id>/slides', methods=('POST',))
@admin_required
def post_slides(meeting_id):
    presenter_id = int(request.form.get('presenter_id', '-1'))
    title = request.form.get('title', None)
    memo = request.form.get('memo', None)
    url = request.form.get('url', None)

    if not title or not url or presenter_id == -1:
        return render_template(
            'form-slides.html', current_user=get_current_user(), meeting_id=meeting_id,
            message='발표자 번호, 제목, URL은 반드시 입력해야합니다.')

    slide = Slide(presenter_id=presenter_id, meeting_id=meeting_id, title=title, memo=memo, url=url)
    db_session.add(slide)
    db_session.commit()

    return redirect(url_for('meetings.get_meeting', meeting_id=meeting_id))
