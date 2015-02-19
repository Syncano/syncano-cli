from ConfigParser import SafeConfigParser

import os
import click
import six

from syncano import connect

from . import settings


class Echo(object):
    '''Object oriented wrapper around Click `secho` function.'''

    def __init__(self, verbose=0):
        self.verbose = verbose

    def __call__(self, message, verbose=None, **style):
        if self.verbose <= 0:
            return

        if verbose and self.verbose < verbose:
            return

        if not isinstance(message, six.string_types):
            message = str(message)

        click.secho(message, **style)

    def error(self, *args, **kwargs):
        kwargs['bold'] = True
        kwargs['fg'] = 'red'
        self(*args, **kwargs)

    def warning(self, *args, **kwargs):
        kwargs['bold'] = True
        kwargs['fg'] = 'yellow'
        self(*args, **kwargs)

    def info(self, *args, **kwargs):
        kwargs['bold'] = False
        kwargs['fg'] = 'blue'
        self(*args, **kwargs)

    def success(self, *args, **kwargs):
        kwargs['bold'] = False
        kwargs['fg'] = 'green'
        self(*args, **kwargs)


class ConfigSection(object):

    def __init__(self, config, section):
        self._config = config
        self._section = section

    def __getattr__(self, k):
        if k.startswith('_'):
            return self.__getattribute__(k)
        return self._config._data[self._section].get(k)

    def __setattr__(self, k, v):
        if k.startswith('_'):
            object.__setattr__(self, k, v)
        else:
            self._config._data[self._section][k] = v

    def __delattr__(self, k):
        if k in self._config._data[self._section]:
            del self._config._data[self._section][k]


class Config(object):

    def __init__(self, filename):
        self.filename = filename
        self._data = {}
        self.read()

    def __getattr__(self, k):
        if k not in self.__dict__:
            if k not in self._data:
                self._data[k] = {}

            section = ConfigSection(self, k)
            setattr(self, k, section)

        return self.__getattribute__(k)

    def __delattr__(self, k):
        if k in self._data:
            del self._data[k]

        object.__delattr__(self, k)

    def clean(self):
        if not self._data:
            return

        for section, options in six.iteritems(self._data):
            if hasattr(self, section):
                delattr(self, section)

    def read(self, filename=None):
        filename = filename or self.filename
        self.clean()

        parser = SafeConfigParser()
        parser.read([filename])
        for section in parser.sections():
            for key, value in parser.items(section):
                self._data.setdefault(section, {})[key] = value

            setattr(self, section, ConfigSection(self, section))
        return self._data

    def save(self, filename=None):
        path = filename or self.filename
        directory, filename = os.path.split(path)

        if not os.path.exists(directory):
            os.makedirs(directory)

        parser = SafeConfigParser()
        for section, options in six.iteritems(self._data):
            parser.add_section(section)
            for name, value in six.iteritems(options):
                parser.set(section, name, value)

        with open(path, 'wb') as f:
            parser.write(f)


class Context(object):

    def __init__(self, config_filename, verbose):
        config_filename = config_filename or settings.CONFIG_DEFAULT_PATH

        self.config = Config(config_filename)
        self.echo = Echo(verbose)

    def is_authenticated(self):
        return self.config.credentials.api_key is not None

    def get_connection(self):
        credentials = self.config.credentials
        return connect(api_key=credentials.api_key)
