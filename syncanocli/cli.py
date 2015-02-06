import click

from . import utils
from . import settings


@click.group(cls=utils.AutodiscoverMultiCommand, context_settings=settings.CONTEXT)
@click.option('--config', '-c', type=click.Path(exists=True, file_okay=True, readable=True),
              callback=utils.read_config, is_eager=True, default=None)
@click.option('--format', '-f', default='text', help='Format for printed output.')
@click.option('--quiet', '-q', default=False, is_flag=True, help='Disable all interactive prompts.')
@click.option('--version', '-v', is_flag=True, callback=utils.print_version, expose_value=False, is_eager=True)
@click.option('--loglevel', '-l', default='NOTSET', type=click.Choice(settings.LOGLEVELS),
              callback=utils.set_loglevel, is_eager=True)
@click.pass_context
def cli(ctx):
    click.echo('nana')


if __name__ == '__main__':
    cli()
