# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask, render_template


def create_app():
    return Flask(__name__)


app = create_app()


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
