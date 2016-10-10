import click
from syncano_cli.base.formatters import ColorStylesE


class Prompter(object):
    indent = '    '

    def prompt(self, text, color=None, **kwargs):
        styles_kwargs = {'fg': color or ColorStylesE.PROMPT}
        return click.prompt(click.style("{}{}".format(self.indent, text), **styles_kwargs), **kwargs)
