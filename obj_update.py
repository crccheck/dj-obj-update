from __future__ import unicode_literals

from operator import itemgetter
import logging
import sys


__all__ = ['obj_update']
__version__ = '0.1.0'


DIRTY = '_is_dirty'


# for python 2/3 compatibility
text_type = unicode if sys.version_info[0] < 3 else str

logger = logging.getLogger('obj_update')


def set_field(obj, field_name, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, field_name)
    # is_relation is Django 1.8 only
    if obj._meta.get_field(field_name).is_relation:
        old_repr = None if old is None else old.pk
        new_repr = None if value is None else value.pk
    else:
        old_repr = None if old is None else text_type(old)
        new_repr = None if value is None else text_type(value)
    if old_repr != new_repr:
        setattr(obj, field_name, value)
        if not hasattr(obj, DIRTY):
            setattr(obj, DIRTY, [])
        getattr(obj, DIRTY).append(dict(
            field_name=field_name,
            old_value=old_repr,
            new_value=new_repr,
        ))


def human_log_formatter(dirty_data):
    return ''.join(
        '[{field_name} {old_value}->{new_value}]'
        .format(**x) for x in dirty_data
    )


def obj_update(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and was saved.
    """
    for field_name, value in data.items():
        set_field(obj, field_name, value)
    dirty_data = getattr(obj, DIRTY, None)
    if dirty_data:
        # WISHLIST ability to also output json events
        logger.debug(human_log_formatter(dirty_data))
        update_fields = list(map(itemgetter('field_name'), dirty_data))
        obj.save(update_fields=update_fields)
        delattr(obj, DIRTY)
        return True


def obj_update_or_create(model, defaults=None, **kwargs):
    """
    Mimic queryset.update_or_create but using obj_update.
    """
    obj, created = model.objects.get_or_create(defaults=defaults, **kwargs)
    if created:
        # TODO logger.debug()
        pass
    else:
        obj_update(obj, defaults)
    return obj, created
