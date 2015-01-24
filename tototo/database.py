# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from tototo import config

db_engine = create_engine(config.DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=db_engine))

Base = declarative_base()
Base.query = db_session.query_property()


class UTCDateTime(TypeDecorator):
    impl = DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, engine):
        if value is not None:
            return value.replace(tzinfo=timezone.utc)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String(32), nullable=False)
    mail_subscribe = Column(Boolean, default=False)

    registered = Column(UTCDateTime, default=datetime.now)


class Meeting(Base):
    __tablename__ = 'meetings'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    location = Column(String(128), nullable=False)
    when = Column(UTCDateTime, nullable=False)
    available = Column(Boolean, default=False)
    quota = Column(Integer, default=0)

    registered = Column(UTCDateTime, default=datetime.now)


class Registration(Base):
    __tablename__ = 'registrations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    status = Column(String(16), default='waiting')  #: waiting, accepted, cancelled, refused
    memo = Column(String(512))

    registered = Column(UTCDateTime, default=datetime.now)
    updated = Column(UTCDateTime, default=datetime.now, onupdate=datetime.now)
