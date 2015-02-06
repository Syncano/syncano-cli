import click

from . import utils
from . import settings


@click.group(cls=utils.AutodiscoverMultiCommand, context_settings=settings.CONTEXT)
@click.option('--config', '-c', type=click.Path(exists=True, file_okay=True, readable=True),
              callback=utils.read_config, is_eager=True, default=None)
@click.option('--version', '-v', is_flag=True, callback=utils.print_version, expose_value=False, is_eager=True)
@click.pass_context
def cli(ctx, *args, **kwargs):
    pass


if __name__ == '__main__':
    cli()
