# -*- coding: utf-8 -*-
import click
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.parse_to_syncano.config import CONFIG_VARIABLES_NAMES


def force_config_value(config, config_var_name, section='P2S'):
    config_var = click.prompt('{}'.format(config_var_name))
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, config_var_name, config_var)


def check_config_value(config, config_var_name, silent, section='P2S'):
    if not config.has_option(section, config_var_name):
        force_config_value(config, config_var_name)
    else:
        if not silent:
            print("{config_var_name}: \t\t{config_var}".format(
                config_var_name=config_var_name,
                config_var=config.get(section, config_var_name)
            ))


def write_config_to_file(config):
    with open(ACCOUNT_CONFIG_PATH, 'wt') as config_file:
        config.write(config_file)


def check_configuration(config, silent=False):
    for config_var_name in CONFIG_VARIABLES_NAMES:
        check_config_value(config, config_var_name, silent=silent)

    write_config_to_file(config)


def force_configuration_overwrite(config):
    for config_var_name in CONFIG_VARIABLES_NAMES:
        force_config_value(config, config_var_name)

    write_config_to_file(config)


def print_configuration(config):
    if not config.has_section('P2S'):
        config.add_section('P2S')
    for config_var_name in CONFIG_VARIABLES_NAMES:
        if not config.has_option('P2S', config_var_name):
            config_var = "-- NOT SET --"
        else:
            config_var = config.get('P2S', config_var_name)

        print("{config_var_name}: \t\t{config_var}".format(
            config_var_name=config_var_name,
            config_var=config_var
        ))
