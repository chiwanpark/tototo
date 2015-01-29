# -*- coding: utf-8 -*-
import os

import click
from alembic import command
from alembic.config import Config
from tototo import app
from tototo.database import Base, db_engine


@click.group()
@click.pass_context
def cli(context):
    context.obj['alembic'] = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))


@cli.command()
@click.option('--port', default=8080)
@click.option('--host', default='0.0.0.0')
def runserver(port, host):
    app.run(host=host, port=port, debug=True)


@cli.command()
@click.pass_context
def db_init(context):
    Base.metadata.drop_all(bind=db_engine)
    context.invoke(db_upgrade, revision='head')


@cli.command()
@click.option('--message', default=None)
@click.pass_context
def db_revision(context, message):
    if not message:
        message = click.prompt('Input commit message', type=str)
    command.revision(context.obj['alembic'], message=message, autogenerate=True)


@cli.command()
@click.option('--revision', default='head')
@click.pass_context
def db_upgrade(context, revision):
    command.upgrade(context.obj['alembic'], revision)


@cli.command()
@click.option('--revision', default='head')
@click.pass_context
def db_downgrade(context, revision):
    command.downgrade(context.obj['alembic'], revision)


if __name__ == '__main__':
    cli(obj={})
