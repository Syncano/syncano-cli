import click
from syncano_cli.account.command import AccountCommands
from syncano_cli.base.options import WarningOpt
from syncano_cli.config import ACCOUNT_CONFIG_PATH


@click.group()
def top_account():
    pass


@top_account.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def accounts(ctx, config):
    """Handle Syncano Account functionality."""
    account_commands = AccountCommands(config_path=config or ACCOUNT_CONFIG_PATH)
    ctx.obj['account_commands'] = account_commands


@accounts.command()
@click.pass_context
def register(ctx):
    """Allows to register new Syncano Account. Email and password are obligatory."""
    account_commands = ctx.obj['account_commands']
    account_commands.output_formatter.write('Create an account in Syncano.', WarningOpt)
    email = account_commands.prompter.prompt('email')
    password = account_commands.prompter.prompt('password', hide_input=True)
    repeat_password = account_commands.prompter.prompt('repeat password', hide_input=True)
    password = account_commands.validate_password(password, repeat_password)
    first_name = account_commands.prompter.prompt('first name (enter to skip)', default='')
    last_name = account_commands.prompter.prompt('last name (enter to skip)', default='')

    account_commands.register(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    account_commands.output_formatter.write('Registration successful for email: {}.'.format(email))
