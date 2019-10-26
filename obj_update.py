"""
`dj-obj-update` helps you update an object but only saves if something changed.
"""

from operator import itemgetter
import datetime as dt
import logging
from unittest.mock import sentinel

__all__ = ["obj_update", "obj_update_or_create"]
__version__ = "0.5.1"


DIRTY = "_is_dirty"
UNSET = sentinel.UNSET


logger = logging.getLogger("obj_update")


def datetime_repr(value):
    if isinstance(value, dt.datetime):
        return value.isoformat().replace("+00:00", "Z")

    return str(value).replace(" ", "T")


def set_field(obj, field_name, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, field_name)
    field = obj._meta.get_field(field_name)
    # is_relation is Django 1.8 only
    if field.is_relation:
        # If field_name is the `_id` field, then there is no 'pk' attr and
        # old/value *is* the pk
        old_repr = None if old is None else getattr(old, "pk", old)
        new_repr = None if value is None else getattr(value, "pk", value)
    elif field.__class__.__name__ == "DateTimeField":
        old_repr = None if old is None else datetime_repr(old)
        new_repr = None if value is None else datetime_repr(value)
    else:
        old_repr = None if old is None else str(old)
        new_repr = None if value is None else str(value)
    if old_repr != new_repr:
        setattr(obj, field_name, value)
        if not hasattr(obj, DIRTY):
            setattr(obj, DIRTY, [])
        getattr(obj, DIRTY).append(
            dict(field_name=field_name, old_value=old_repr, new_value=new_repr)
        )


def human_log_formatter(dirty_data):
    return "".join(
        "[{field_name} {old_value}->{new_value}]".format(**x) for x in dirty_data
    )


def json_log_formatter(dirty_data):
    return {
        x["field_name"]: {"old": x["old_value"], "new": x["new_value"]}
        for x in dirty_data
    }


def obj_update(obj, data: dict, *, update_fields=UNSET, save: bool = True) -> bool:
    """
    Fancy way to update `obj` with `data` dict.

    Parameters
    ----------
    obj : Django model instance
    data
        The data to update ``obj`` with
    update_fields
        Use your ``update_fields`` instead of our generated one. If you need
        an auto_now or auto_now_add field to get updated, set this to ``None``
        to get the default Django behavior.
    save
        If save=False, then don't actually save. This can be useful if you
        just want to utilize the verbose logging.
        DEPRECRATED in favor of the more standard ``update_fields=[]``

    Returns
    -------
    bool
        True if data changed
    """
    for field_name, value in data.items():
        set_field(obj, field_name, value)
    dirty_data = getattr(obj, DIRTY, None)
    if not dirty_data:
        return False

    logger.debug(
        human_log_formatter(dirty_data),
        extra={
            "model": obj._meta.object_name,
            "pk": obj.pk,
            "changes": json_log_formatter(dirty_data),
        },
    )
    if update_fields == UNSET:
        update_fields = list(map(itemgetter("field_name"), dirty_data))
    if not save:
        update_fields = ()
    obj.save(update_fields=update_fields)
    delattr(obj, DIRTY)
    return True


def obj_update_or_create(model, defaults=None, update_fields=UNSET, **kwargs):
    """
    Mimic queryset.update_or_create but using obj_update.
    """
    obj, created = model.objects.get_or_create(defaults=defaults, **kwargs)
    if created:
        logger.debug(
            "CREATED %s %s", model._meta.object_name, obj.pk, extra={"pk": obj.pk}
        )
    else:
        obj_update(obj, defaults, update_fields=update_fields)
    return obj, created
