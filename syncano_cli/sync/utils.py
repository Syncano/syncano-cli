# coding=UTF8
from __future__ import print_function, unicode_literals


def compare_dicts(new, old):
    """
    Compare two dicts returning same, added, removed, modified elements as lists
    """
    new_keys = set(new.keys())
    if not old:
        return None, set(new.keys()), None, None
    old_keys = set(old.keys())
    intersect_keys = new_keys.intersection(old_keys)
    added = new_keys - old_keys
    removed = old_keys - new_keys
    modified = {o: (new[o], old[o]) for o in intersect_keys if new[o] != old[o]}
    same = set(o for o in intersect_keys if new[o] == old[o])
    return same, added, removed, modified
