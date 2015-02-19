import click
from texttable import Texttable

from syncano.models.base import Instance
from syncano.exceptions import (
    SyncanoRequestError, SyncanoValidationError,
    SyncanoDoesNotExist
)

from syncanocli.utils import (
    login_required, model_options, model_endpoint_fields,
    model_fields_option
)


@click.group('instances', invoke_without_command=True)
@model_fields_option(Instance)
@click.pass_context
@login_required
def cli(ctx, fields):
    '''List and manage your instances.'''
    if ctx.invoked_subcommand:
        return

    ctx = ctx.obj
    connection = ctx.get_connection()
    instances = connection.instances.all()
    headres = [f.label for f in fields]
    table = Texttable()
    table.header(headres)
    for i, instance in enumerate(instances, 1):
        table.add_row([getattr(instance, f.name) for f in fields])

        if i % 10 == 0:
            ctx.echo(table.draw())
            table.reset()
            table.header(headres)
            click.confirm('More?', default=True, abort=True)

    ctx.echo(table.draw())


@cli.command()
@click.pass_obj
@login_required
@model_options(Instance)
def create(ctx, **kwargs):
    '''Create a new instance.'''
    connection = ctx.get_connection()
    try:
        instance = connection.instances.create(**kwargs)
    except (SyncanoRequestError, SyncanoValidationError) as e:
        ctx.echo.error(e)
    else:
        ctx.echo.success('Instance successfully created: {0}!'.format(instance.pk))


@cli.command()
@click.pass_obj
@login_required
@model_fields_option(Instance)
@model_endpoint_fields(Instance)
def retrieve(ctx, **kwargs):
    '''Retrieve details about instance.'''
    fields = kwargs.pop('fields', [])
    connection = ctx.get_connection()
    try:
        instance = connection.instances.get(**kwargs)
    except (SyncanoRequestError, SyncanoValidationError) as e:
        ctx.echo.error(e)
    except SyncanoDoesNotExist as e:
        ctx.echo.error('Instance does not exist.')
    else:
        rows = [(f.label, f.to_native(getattr(instance, f.name))) for f in fields]
        table = Texttable()
        table.header(['Field', 'Value'])
        table.add_rows(rows, header=False)
        ctx.echo(table.draw())


@cli.command()
@click.pass_obj
@login_required
@model_options(Instance)
def update(ctx, **kwargs):
    pass


@cli.command()
@click.pass_obj
@login_required
@model_endpoint_fields(Instance)
def destroy(ctx, **kwargs):
    connection = ctx.get_connection()
    try:
        connection.instances.delete(**kwargs)
    except (SyncanoRequestError, SyncanoValidationError) as e:
        ctx.echo.error(e)
    else:
        ctx.echo.success('Instance successfully destroyed!')
