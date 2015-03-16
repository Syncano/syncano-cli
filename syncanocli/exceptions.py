from click import style
from click.exceptions import ClickException, get_text_stderr
from click.utils import echo


class SyncanoCliException(ClickException):
    """
    An exception that Click can handle and show to the user.

    :param message: the error message to display.
    :param hint: the hint message to display.
    """

    message = None
    hint = None

    def __init__(self, message=None, hint=None):
        self.message = message or self.message
        self.hint = hint or self.hint
        super(SyncanoCliException, self).__init__(self.message)

    def format_message(self):
        return style(self.message, fg='red', bold=True)

    def format_hint(self):
        return self.hint

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()

        echo(self.format_message(), file=file)
        if self.hint is not None:
            echo(self.format_hint(), file=file)


class NotAuthenticatedError(SyncanoCliException):
    """
    An internal exception that signals an authentication error.
    This typically aborts any further handling.
    """
    message = 'You are not authenticated.'
    hint = 'Try to login via "syncano login" command.'
