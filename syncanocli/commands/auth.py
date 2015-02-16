import click

from syncano.connection import Connection
from syncano.exceptions import SyncanoRequestError


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
    ctx.echo.success('Done!')


@cli.command()
@click.pass_obj
def logout(ctx):
    '''Clear local authentication credentials'''
    del ctx.config.credentials
    ctx.config.save()
    ctx.echo.success('Done!')


@cli.command()
@click.pass_obj
def api_key(ctx):
    '''Display your current api key'''
    if ctx.is_authenticated():
        ctx.echo(ctx.config.credentials.api_key)
    else:
        ctx.echo.error('You are not authenticated.')


@cli.command()
@click.pass_obj
def whoami(ctx):
    '''Display your Syncano email address'''
    if ctx.is_authenticated():
        message = 'You are logged in as {0} with API key: {1}'
        credentials = ctx.config.credentials
        ctx.echo(message.format(credentials.email, credentials.api_key))
    else:
        ctx.echo.error('You are not authenticated.')
