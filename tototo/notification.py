# -*- coding: utf-8 -*-
from flask import render_template
from sendgrid import SendGridClient, Mail
from tototo import config
from tototo.database import User


def send_email_to_user(user: User, subject: str, template: str, values: dict) -> bool:
    return send_email(user.name, user.email, subject, template, values)


def send_email(name: str, address: str, subject: str, template: str, values: dict) -> bool:
    sg = SendGridClient(config.SENDGRID_API_USER, config.SENDGRID_API_KEY)

    mail = Mail()
    mail.set_from('tototo <tototo-no-reply@chiwanpark.com>')
    mail.add_to(name + ' <' + address + '>')
    mail.set_subject(subject)
    mail.set_html(render_template(template, **values))

    status, _ = sg.send(mail)

    return status == 200
