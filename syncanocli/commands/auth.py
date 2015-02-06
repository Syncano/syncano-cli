import click


@click.command('auth')
def cli(*args, **kwargs):
    print 'aith', args, kwargs
