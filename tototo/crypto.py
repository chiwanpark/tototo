# -*- coding: utf-8 -*-
from datetime import datetime

import bcrypt
from flask import json
from tototo import config


def _build_payload(value: str, purpose: str, expired: datetime=None) -> str:
    payload = {'value': value, 'purpose': purpose, 'expired': expired.strftime(config.DATETIME_FORMAT)}
    return json.dumps(payload)


def create_token(value: str, purpose: str, expired: datetime=None) -> str:
    payload = _build_payload(value, purpose, expired).encode('utf-8')
    return bcrypt.hashpw(payload, bcrypt.gensalt()).decode('utf-8')


def valid_token(token: str, value: str, purpose: str, expired: datetime=None) -> bool:
    payload = _build_payload(value, purpose, expired).encode('utf-8')
    token = token.encode('utf-8')

    try:
        return bcrypt.hashpw(payload, token) == token
    except:
        return False
