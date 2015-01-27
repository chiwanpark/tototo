# -*- coding: utf-8 -*-
from tototo.endpoints import users, meetings, index


def get_blueprints():
    return [users.context, meetings.context, index.context]
