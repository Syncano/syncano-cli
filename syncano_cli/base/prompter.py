import click
from syncano_cli.base.output_formatter import ColorStylesE


class Prompter(object):
    indent = '    '

    def prompt(self, text, color=None, **kwargs):
        styles_kwargs = {'fg': color or ColorStylesE.PROMPT}
        click.echo()
        return click.prompt(click.style("{}{}".format(self.indent, text), **styles_kwargs), **kwargs)
