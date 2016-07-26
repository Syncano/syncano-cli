# coding=UTF8
from __future__ import print_function, unicode_literals


def compare_dicts(new, old):
    """
    Compare two dicts returning same, added, removed, modified elements as lists
    """
    old_keys = set(old or ())
    new_keys = set(new or ())
    common = new_keys & old_keys
    added = new_keys - old_keys
    removed = old_keys - new_keys
    same = set(k for k in common if old[k] == new[k])
    return same, added, removed, common - same
