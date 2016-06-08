# -*- coding: utf-8 -*-
import logging

_LOGGERS = {}


def get_logger(name):
    if name not in _LOGGERS:
        _LOGGERS[name] = _create_logger(name)
    return _LOGGERS[name]


def _create_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    return logger
