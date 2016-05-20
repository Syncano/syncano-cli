# -*- coding: utf-8 -*-

from syncano_cli.parse_to_syncano.config import CONFIG_VARIABLES_NAMES, P2S_CONFIG_PATH, config


def force_config_value(config_var_name, section='P2S'):
    config_var = raw_input('{}: '.format(config_var_name))
    config.set(section, config_var_name, config_var)


def check_config_value(config_var_name, silent, section='P2S'):
    config_var = config.get(section, config_var_name)
    if not config_var:
        force_config_value(config_var_name, section)
    else:
        if not silent:
            print("{config_var_name}: \t\t{config_var}".format(
                config_var_name=config_var_name,
                config_var=config_var
            ))


def write_config_to_file():
    with open(P2S_CONFIG_PATH, 'wb') as config_file:
        config.write(config_file)


def check_configuration(silent=False):
    for config_var_name in CONFIG_VARIABLES_NAMES:
        check_config_value(config_var_name, silent=silent)

    write_config_to_file()


def force_configuration_overwrite():
    for config_var_name in CONFIG_VARIABLES_NAMES:
        force_config_value(config_var_name)

    write_config_to_file()


def print_configuration():
    for config_var_name in CONFIG_VARIABLES_NAMES:
        print("{config_var_name}: \t\t{config_var}".format(
            config_var_name=config_var_name,
            config_var=config.get('P2S', config_var_name) or "-- NOT SET --"
        ))
