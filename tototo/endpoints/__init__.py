# -*- coding: utf-8 -*-
from tototo.endpoints import users, meetings


def get_blueprints():
    return [users.context, meetings.context]
