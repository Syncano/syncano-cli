# -*- coding: utf-8 -*-


class BaseInstanceCommand(object):

    def __init__(self, instance):
        """
        A command that stores direct Instance connection;
        :param instance: the Syncano Instance object;
        """
        self.instance = instance


class BaseConnectionCommand(object):

    def __init__(self, connection):
        """
        A command that stores general connection;
        :param connection: the Syncano connection object;
        """
        self.connection = connection
