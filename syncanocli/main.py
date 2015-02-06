import click

from .utils import print_version, set_loglevel


LOGLEVEL_CHOICES = [
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
    'NOTSET',
]


@click.group()
@click.option('--config', '-c', default='~/.syncano', help='Syncano config file.')
@click.option('--format', '-f', default='text', help='Format for printed output.')
@click.option('--quiet', '-q', default=False, is_flag=True, help='Disable all interactive prompts.')
@click.option('--version', '-v', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.option('--loglevel', '-l', default='NOTSET', type=click.Choice(LOGLEVEL_CHOICES),
              callback=set_loglevel, is_eager=True)
@click.pass_context
def cli(ctx):
    click.echo('nana')


if __name__ == '__main__':
    cli()
