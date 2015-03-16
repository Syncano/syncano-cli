from click import style
from click.exceptions import ClickException, get_text_stderr
from click.utils import echo


class SyncanoCliException(ClickException):
    """
    An internal exception that signals a authentication error.
    This typically aborts any further handling.

    :param message: the error message to display.
    :param hint: the hint message to display.
    """

    message = None
    hint = None

    def __init__(self, message=None, hint=None):
        self.message = message or self.message
        self.hint = hint or self.hint
        super(SyncanoCliException, self).__init__(self.message)

    def format_hint(self):
        return self.hint

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()

        echo(style(self.format_message(), fg='red', bold=True), file=file)
        if self.hint is not None:
            echo(self.format_hint(), file=file)


class NotAuthenticatedError(SyncanoCliException):
    """
    An internal exception that signals a authentication error.
    This typically aborts any further handling.
    """
    message = 'You are not authenticated.'
    hint = 'Try to login via "syncano auth login" command.'
