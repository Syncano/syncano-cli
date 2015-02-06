import click
import syncanocli


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(syncanocli.__version__)
    ctx.exit()
