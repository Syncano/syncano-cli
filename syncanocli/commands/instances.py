import click
import six
from texttable import Texttable

from syncano.models.base import Instance

from syncanocli.decorators import (
    login_required, model, model_fields_option,
    model_options, model_arguments,
)


@click.group('instances', invoke_without_command=True)
@click.option('--page-size', default=10, show_default=True)
@click.pass_context
@login_required
@model(Instance)
@model_fields_option(Instance)
def cli(ctx, fields, page_size):
    '''List and manage your instances.'''
    if ctx.invoked_subcommand:
        return

    ctx = ctx.obj
    instances = ctx.list(page_size)
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
@model(Instance)
@model_options(Instance)
def create(ctx, **kwargs):
    '''Create a new instance.'''
    ctx.create(**kwargs)


@cli.command()
@click.pass_obj
@login_required
@model(Instance)
@model_arguments(Instance)
@model_fields_option(Instance)
def details(ctx, **kwargs):
    '''Details about instance.'''
    fields = kwargs.pop('fields', [])
    instance = ctx.details(**kwargs)
    rows = [(f.label, f.to_native(getattr(instance, f.name))) for f in fields]
    table = Texttable()
    table.header(['Field', 'Value'])
    table.add_rows(rows, header=False)
    ctx.echo(table.draw())


@cli.command()
@click.pass_obj
@login_required
@model(Instance)
@model_arguments(Instance)
@model_options(Instance, prompt=False, required=False)
def update(ctx, **kwargs):
    model = ctx.model
    query = {k: v for k, v in six.iteritems(kwargs) if k in model._meta.endpoint_fields}
    data = {k: v for k, v in six.iteritems(kwargs) if k not in query}
    instance = ctx.details(**query)

    for k, v in six.iteritems(data):
        if v:
            continue

        default = getattr(instance, k, None)
        data[k] = click.prompt('Set {0}'.format(k), default=default)

    diff = {k: v for k, v in six.iteritems(data) if getattr(instance, k, None) != v}
    if not diff:
        ctx.echo.info('Nothing to update, Bye!')
        return

    query['data'] = diff
    ctx.update(**query)


@cli.command()
@click.pass_obj
@click.confirmation_option(prompt='Are you sure you want to remove this instance?')
@login_required
@model(Instance)
@model_arguments(Instance)
def remove(ctx, **kwargs):
    '''Remove selected instance.'''
    ctx.remove(**kwargs)
