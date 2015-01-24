# -*- coding: utf-8 -*-
from datetime import datetime
import importlib

from flask import Flask, render_template
from tototo import config
from tototo.database import db_session


def create_app():
    blueprints = ['users']
    context = Flask(__name__)

    for blueprint in blueprints:
        try:
            module = importlib.import_module('tototo.{blueprint}'.format(blueprint=blueprint))
            context.register_blueprint(module.context)
        except ImportError as ex:
            pass

    return context


app = create_app()
app.config['DATABASE_URI'] = config.DATABASE_URI
app.config['SECRET_KEY'] = config.SECRET_KEY


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    sample = {
        'next_toz': dict(date=datetime.now(), location='토즈 강남토즈타워점'),
        'prev_toz': [
            dict(date=datetime.now(), location='토즈 강남토즈타워점', people=['박치완', '한진수']),
            dict(date=datetime.now(), location='토즈 강남토즈타워점', people=['박치완', '한진수', '한륜희']),
            dict(date=datetime.now(), location='토즈 강남토즈타워점', people=['박치완', '김승원'])
        ]
    }

    return render_template('index.html', **sample)
