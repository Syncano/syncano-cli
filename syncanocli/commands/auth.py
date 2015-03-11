import click

from syncano.connection import Connection
from syncano.exceptions import SyncanoRequestError

from syncanocli.decorators import login_required


@click.group('auth')
def cli(*args, **kwargs):
    '''Authenticate, display api key and current user'''


@cli.command()
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.pass_obj
def login(ctx, email, password):
    '''Log in with your Syncano credentials'''
    connection = Connection()
    try:
        api_key = connection.authenticate(email=email, password=password)
    except SyncanoRequestError as e:
        ctx.echo.error(e.reason)
        return

    ctx.config.credentials.email = email
    ctx.config.credentials.api_key = api_key
    ctx.config.save()
    ctx.echo.success('Authentication successful!')


@cli.command()
@click.pass_obj
@login_required
def logout(ctx):
    '''Clear local authentication credentials'''
    del ctx.config.credentials
    ctx.config.save()
    ctx.echo.success('Done!')


@cli.command()
@click.pass_obj
@login_required
def api_key(ctx):
    '''Display your current api key'''
    ctx.echo(ctx.config.credentials.api_key)


@cli.command()
@click.pass_obj
@login_required
def whoami(ctx):
    '''Display your Syncano email address'''
    message = 'You are logged in as {0} with API key: {1}'
    credentials = ctx.config.credentials
    ctx.echo(message.format(credentials.email, credentials.api_key))
