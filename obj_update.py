from __future__ import unicode_literals

import logging
import sys


# for python 2/3 compatibility
text_type = unicode if sys.version_info[0] < 3 else str

logger = logging.getLogger('obj_update')


def setfield(obj, fieldname, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, fieldname)
    if old is None and value is None:
        changed = False
    elif old is None and value is not None:
        changed = True
    else:
        changed = text_type(old) != text_type(value)
    if changed:
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
            obj._dirty_fields = []
        # obj._is_dirty.append(u'[%s %s->%s]' % (fieldname, old, value))
        obj._is_dirty.append(fieldname)
        obj._dirty_fields.append(fieldname)


def set_foreign_field(obj, fieldname, value):
    """Fancy setattr with debugging for foreign fields."""
    old = getattr(obj, fieldname)
    old_repr = old if old is None else old.pk
    new_repr = value if value is None else value.pk
    if old_repr != new_repr:
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
            obj._dirty_fields = []
        obj._is_dirty.append('[%s %s->%s]' % (fieldname, old_repr, new_repr))
        obj._dirty_fields.append(fieldname)


def update(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and was saved.
    """
    for field_name, value in data.items():
        # is_relation is Django 1.8 only
        if obj._meta.get_field(field_name).is_relation:
            set_foreign_field(obj, field_name, value)
        else:
            setfield(obj, field_name, value)
    if getattr(obj, '_is_dirty', None):
        logger.debug(u''.join(obj._is_dirty))
        obj.save(update_fields=obj._dirty_fields)
        del obj._is_dirty
        del obj._dirty_fields
        return True
