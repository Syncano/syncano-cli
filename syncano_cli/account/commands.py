import click
from syncano_cli.account.command import AccountCommands
from syncano_cli.config import ACCOUNT_CONFIG_PATH


@click.group()
def top_account():
    pass


@top_account.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def accounts(ctx, config):
    """Handle Syncano account functionality."""
    account_commands = AccountCommands(config_path=config or ACCOUNT_CONFIG_PATH)
    ctx.obj['account_commands'] = account_commands


@accounts.command()
@click.pass_context
@click.argument('email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--first-name', help=u'First name of the user.')
@click.option('--last-name', help=u'Last name of the user.')
@click.option('--invitation-key', help=u'Invitation key.')
def register(ctx, email, password, first_name, last_name, invitation_key):
    ctx.obj['account_commands'].register(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        invitation_key=invitation_key
    )
    click.echo('INFO: Registration successful.')
