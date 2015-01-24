# -*- coding: utf-8 -*-
import click
from tototo import app
from tototo.database import Base, db_engine


@click.group()
def cli():
    pass


@cli.command()
@click.option('--port', default=8080)
@click.option('--host', default='0.0.0.0')
def runserver(port, host):
    app.run(host=host, port=port, debug=True)

@cli.command()
def init_db():
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)


if __name__ == '__main__':
    cli()
