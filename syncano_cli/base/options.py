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

    def __init__(
            self,
            color=ColorSchema.INFO,
            indent=1,
            space_top=False,
            space_bottom=False):
        """Allows to override class attributes."""
        self.color = color
        self.indent = indent
        self.space_top = space_top
        self.space_bottom = space_bottom

    def map_click(self):
        return {click_name: getattr(self, option_name) for option_name, click_name in six.iteritems(self.CLICK_MAP)}

    def get_options(self):
        return {
            key: value for key, value in six.iteritems(self.__dict__) if key in self.OPTIONS
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
    OPTIONS = ['color']

    def __init__(self, color=ColorSchema.ERROR, **kwargs):
        super(ErrorOpt, self).__init__(color=color, **kwargs)


class WarningOpt(OptionsBase):
    OPTIONS = ['color']

    def __init__(self, color=ColorSchema.WARNING, **kwargs):
        super(WarningOpt, self).__init__(color=color, **kwargs)


class PromptOpt(OptionsBase):
    OPTIONS = ['color']

    def __init__(self, color=ColorSchema.PROMPT, **kwargs):
        super(PromptOpt, self).__init__(color=color, **kwargs)


class TopSpacedOpt(OptionsBase):
    OPTIONS = ['space_top']

    def __init__(self, space_top=True, **kwargs):
        super(TopSpacedOpt, self).__init__(space_top=space_top, **kwargs)


class BottomSpacedOpt(OptionsBase):
    OPTIONS = ['space_bottom']

    def __init__(self, space_bottom=True, **kwargs):
        super(BottomSpacedOpt, self).__init__(space_bottom=space_bottom, **kwargs)


class SpacedOpt(OptionsBase):
    OPTIONS = ['space_top', 'space_bottom']

    def __init__(self, space_top=True, space_bottom=True, **kwargs):
        super(SpacedOpt, self).__init__(space_top=space_top, space_bottom=space_bottom, **kwargs)
