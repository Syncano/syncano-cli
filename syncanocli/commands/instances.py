import click
from texttable import Texttable

from syncano.models.base import Instance
from syncano.exceptions import (
    SyncanoRequestError, SyncanoValidationError,
    SyncanoDoesNotExist
)

from syncanocli.decorators import (
    login_required, model_options, model_endpoint_options,
    model_fields_option, model_update_options
)


@click.group('instances', invoke_without_command=True)
@model_fields_option(Instance)
@click.option('--page-size', default=10, show_default=True)
@click.pass_context
@login_required
def cli(ctx, fields, page_size):
    '''List and manage your instances.'''
    if ctx.invoked_subcommand:
        return

    ctx = ctx.obj
    connection = ctx.get_connection()
    instances = connection.instances.page_size(page_size).all()
    headres = [f.label for f in fields]
    table = Texttable()
    table.header(headres)
    for i, instance in enumerate(instances, 1):
        table.add_row([getattr(instance, f.name) for f in fields])

        if i % page_size == 0:
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
@model_endpoint_options(Instance)
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
@model_endpoint_options(Instance)
@model_update_options(Instance)
def update(ctx, **kwargs):
    pass


@cli.command()
@click.pass_obj
@login_required
@click.confirmation_option(prompt='Are you sure you want to destroy this instance?')
@model_endpoint_options(Instance)
def destroy(ctx, **kwargs):
    '''Destroy selected instance.'''
    connection = ctx.get_connection()
    try:
        connection.instances.delete(**kwargs)
    except (SyncanoRequestError, SyncanoValidationError) as e:
        ctx.echo.error(e)
    else:
        ctx.echo.success('Instance successfully destroyed!')
