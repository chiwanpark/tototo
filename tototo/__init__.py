# -*- coding: utf-8 -*-
import importlib

from flask import Flask
from tototo import config, util
from tototo.database import db_session


def create_app():
    context = Flask(__name__)

    try:
        endpoints = importlib.import_module('tototo.endpoints')
        for blueprint in endpoints.get_blueprints():
            context.register_blueprint(blueprint)
    except ImportError as ex:
        pass

    return context


app = create_app()
app.config['DATABASE_URI'] = config.DATABASE_URI
app.config['SECRET_KEY'] = config.SECRET_KEY
app.jinja_env.filters['localtime_format'] = util.localtime_format


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
