# -*- coding: utf-8 -*-
import click
from tototo import app


@click.group()
def cli():
    pass


@cli.command()
@click.option('--port', default=8080)
@click.option('--host', default='0.0.0.0')
def runserver(port, host):
    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    cli()
