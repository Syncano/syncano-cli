import click
from syncano_cli.account.command import AccountCommands
from syncano_cli.base.options import SpacedOpt


@click.group()
def top_account():
    pass


@top_account.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def accounts(ctx, config):
    """Handle Syncano Account functionality."""
    account_commands = AccountCommands(config, force_register=True)
    ctx.obj['account_commands'] = account_commands


@accounts.command()
@click.pass_context
def register(ctx):
    """Allows to register new Syncano Account. Email and password are obligatory."""
    account_commands = ctx.obj['account_commands']
    email = account_commands.config.get_config('DEFAULT', 'email')
    account_commands.formatter.write('Registration successful for email: {}.'.format(email), SpacedOpt())
