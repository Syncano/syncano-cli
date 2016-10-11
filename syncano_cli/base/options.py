# -*- coding: utf-8 -*-
import six


class ColorSchema(object):
    INFO = 'green'
    PROMPT = 'cyan'
    WARNING = 'yellow'
    ERROR = 'red'


class OptionsBase(object):
    CLICK_MAP = {
        'color': 'fg'
    }

    OPTIONS = ['color', 'indent', 'space_top', 'space_bottom']

    def __init__(self, color, indent, space_top, space_bottom):
        """Allows to override class attributes."""
        self.color = color
        self.indent = indent
        self.space_top = space_top
        self.space_bottom = space_bottom

    def map_click(self):
        return {click_name: getattr(self, option_name) for option_name, click_name in six.iteritems(self.CLICK_MAP)}

    @classmethod
    def get_options(cls):
        return {
            key: value for key, value in six.iteritems(cls.__dict__) if key in cls.OPTIONS
        }

    @classmethod
    def build_options(cls, option_list):
        options = {}
        for option in option_list:
            options.update(option.get_options())
        return cls(**options)


class DefaultOpt(OptionsBase):
    color = ColorSchema.INFO
    indent = 1
    space_top = False
    space_bottom = False


class ErrorOpt(OptionsBase):
    color = ColorSchema.ERROR


class WarningOpt(OptionsBase):
    color = ColorSchema.WARNING


class PromptOpt(OptionsBase):
    color = ColorSchema.PROMPT


class TopSpacedOpt(OptionsBase):
    space_top = True


class BottomSpacedOpt(OptionsBase):
    space_bottom = True


class SpacedOpt(TopSpacedOpt, BottomSpacedOpt):
    pass
