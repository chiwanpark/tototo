# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, func, text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, configure_mappers
from tototo import config


db_engine = create_engine(config.DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(bind=db_engine))

Base = declarative_base()
Base.query = db_session.query_property()


def datetime_now():
    return config.TIMEZONE.localize(datetime.now())


def init_schema():
    configure_mappers()
    Base.metadata.create_all(bind=db_engine)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    email = Column(String(256), nullable=False, unique=True)
    mail_subscribe = Column(Boolean, default=False)

    hashed_password = Column(String(60), nullable=False)

    registered = Column(DateTime(timezone=True), default=datetime_now)

    class CryptComparator(Comparator):
        def __eq__(self, other):
            return self.expression == func.crypt(other, self.expression)

    @hybrid_property
    def password(self):
        raise NotImplementedError('password cannot be accessed.')

    @password.setter
    def password(self, value):
        self.hashed_password = func.crypt(value, func.gen_salt('bf'))

    @password.comparator
    def password(cls):
        return User.CryptComparator(cls.hashed_password)

    class IsAdminComparator(Comparator):
        def __eq__(self, other):
            return (self.expression == 1) == other

    @hybrid_property
    def is_admin(self):
        return self.id == 1

    @is_admin.setter
    def is_admin(self, value):
        raise NotImplementedError('is_admin is a readonly property')

    @is_admin.comparator
    def is_admin(cls):
        return User.IsAdminComparator(cls.id)

    registrations = relationship('Registration', lazy='dynamic')


class Meeting(Base):
    __tablename__ = 'meetings'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    where = Column(String(128), nullable=False)
    when = Column(DateTime(timezone=True), nullable=False)
    when_end = Column(DateTime(timezone=True), default=datetime_now, nullable=False)
    available = Column(Boolean, default=False)
    location_lat = Column(Float, default=0.0, server_default=text('0.0'))
    location_lng = Column(Float, default=0.0, server_default=text('0.0'))
    quota = Column(Integer, default=0)

    registered = Column(DateTime(timezone=True), default=datetime_now)

    @hybrid_property
    def users(self):
        registrations = db_session.query(Registration).filter(Registration.meeting_id == self.id, Registration.status == 'accepted')
        return [registration.user for registration in registrations]

    def status_of(self, user: User) -> str:
        registration = db_session.query(Registration).filter(Registration.meeting == self, Registration.user == user).first()
        if not registration:
            return 'not-registered'
        return registration.status

    registrations = relationship('Registration', lazy='dynamic')
    slides = relationship('Slide', lazy='dynamic')


class Registration(Base):
    __tablename__ = 'registrations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    status = Column(String(16), default='waiting')  #: waiting, accepted, cancelled, refused
    memo = Column(String(512))

    registered = Column(DateTime(timezone=True), default=datetime_now)
    updated = Column(DateTime(timezone=True), default=datetime_now, onupdate=datetime_now)

    meeting = relationship('Meeting')
    user = relationship('User')


class Slide(Base):
    __tablename__ = 'slides'
    id = Column(Integer, primary_key=True)
    presenter_id = Column(Integer, ForeignKey('users.id'))
    meeting_id = Column(Integer, ForeignKey('meetings.id'))

    title = Column(String(512), nullable=False)
    memo = Column(String(512))
    url = Column(String(1024))

    registered = Column(DateTime(timezone=True), default=datetime_now)
    updated = Column(DateTime(timezone=True), default=datetime_now, onupdate=datetime_now)

    meeting = relationship('Meeting')
    presenter = relationship('User')
