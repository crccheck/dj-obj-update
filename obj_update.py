from __future__ import unicode_literals

from operator import itemgetter
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
        obj._is_dirty.append(dict(
            field_name=field_name,
            old_value=old_repr,
            new_value=new_repr,
        ))


def human_log_formatter(dirty_data):
    return ''.join(
        '[{field_name} {old_value}->{new_value}]'
        .format(**x) for x in dirty_data
    )


def update(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and was saved.
    """
    for field_name, value in data.items():
        set_field(obj, field_name, value)
    dirty_data = getattr(obj, '_is_dirty', None)
    if dirty_data:
        # WISHLIST ability to also output json events
        logger.debug(human_log_formatter(dirty_data))
        update_fields = map(itemgetter('field_name'), dirty_data)
        obj.save(update_fields=update_fields)
        delattr(obj, '_is_dirty')
        return True
