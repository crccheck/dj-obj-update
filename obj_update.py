from __future__ import unicode_literals

import logging
import sys


# for python 2/3 compatibility
text_type = unicode if sys.version_info[0] < 3 else str

logger = logging.getLogger('obj_update')


def set_field(obj, field_name, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, field_name)
    # is_relation is Django 1.8 only
    if obj._meta.get_field(field_name).is_relation:
        old_repr = old if old is None else old.pk
        new_repr = value if value is None else value.pk
    else:
        old_repr = old if old is None else text_type(old)
        new_repr = value if value is None else text_type(value)
    if old_repr != new_repr:
        setattr(obj, field_name, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
            obj._dirty_fields = []
        obj._is_dirty.append('[%s %s->%s]' % (field_name, old_repr, new_repr))
        obj._dirty_fields.append(field_name)


def update(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and was saved.
    """
    for field_name, value in data.items():
        set_field(obj, field_name, value)
    if getattr(obj, '_is_dirty', None):
        logger.debug(u''.join(obj._is_dirty))
        obj.save(update_fields=obj._dirty_fields)
        del obj._is_dirty
        del obj._dirty_fields
        return True
