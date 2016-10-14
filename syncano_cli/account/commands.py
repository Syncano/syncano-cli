import click
from syncano_cli.account.command import AccountCommands
from syncano_cli.base.options import ColorSchema, SpacedOpt, WarningOpt


@click.group()
def top_account():
    pass


@top_account.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def accounts(ctx, config):
    """Handle Syncano Account functionality."""
    account_commands = AccountCommands(config)
    ctx.obj['account_commands'] = account_commands


@accounts.command()
@click.pass_context
def register(ctx):
    """Allows to register new Syncano Account. Email and password are obligatory."""
    account_commands = ctx.obj['account_commands']
    account_commands.formatter.write('Create an account in Syncano.', SpacedOpt(), WarningOpt())
    email = account_commands.prompter.prompt('email')
    password = account_commands.prompter.prompt('password', hide_input=True)
    repeat_password = account_commands.prompter.prompt('repeat password', hide_input=True)
    password = account_commands.validate_password(password, repeat_password)
    first_name = account_commands.prompter.prompt('first name (enter to skip)', default='', show_default=False)
    last_name = account_commands.prompter.prompt('last name (enter to skip)', default='', show_default=False)

    account_commands.register(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    account_commands.formatter.write('Registration successful for email: {}.'.format(email), SpacedOpt())
    account_commands.formatter.write("{}: `{}`".format(
        click.style('Create your first instance now', fg=ColorSchema.INFO),
        click.style('syncano instances create my-new-instance', fg=ColorSchema.WARNING)
    ), SpacedOpt())
