import click


@click.group('auth')
def cli(*args, **kwargs):
    '''Authenticate, display api key and current user'''


@cli.command()
def login():
    '''Log in with your Syncano credentials'''


@cli.command()
def logout():
    '''Clear local authentication credentials'''


@cli.command()
def api_key():
    '''Display your current api key'''


@cli.command()
def whoami():
    '''Display your Syncano email address'''
