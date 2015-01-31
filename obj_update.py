import logging

logger = logging.getLogger('obj_update')


def setfield(obj, fieldname, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, fieldname)
    if str(old) != str(value):
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
        obj._is_dirty.append("%s %s->%s" % (fieldname, old, value))


def update(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and  was saved.
    """
    for key, value in data.items():
        setfield(obj, key, value)
    if getattr(obj, '_is_dirty', None):
        logger.debug(obj._is_dirty)
        obj.save()
        del obj._is_dirty
        return True


def setfield(obj, fieldname, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, fieldname)
    if hasattr(old, 'pk'):
        # foreign key comparison
        changed = old.pk != value.pk
    else:
        changed = str(old) != str(value)
    if changed:
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
            obj._dirty_fields = []
        obj._is_dirty.append("%s %s->%s" % (fieldname, old, value))
        obj._dirty_fields.append(fieldname)


def update_with_defaults(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and  was saved.
    """
    for key, value in data.items():
        setfield(obj, key, value)
    if getattr(obj, '_is_dirty', None):
        logger.debug(obj._is_dirty)
        obj.save(update_fields=obj._dirty_fields)
        del obj._is_dirty
        del obj._dirty_fields
        return True
