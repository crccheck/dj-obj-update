import logging
import sys


# for python 2/3 compatibility
text_type = unicode if sys.version_info[0] < 3 else str

logger = logging.getLogger('obj_update')


def setfield(obj, fieldname, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, fieldname)
    # print old, value
    if hasattr(old, 'pk'):
        if value is None:
            changed = True
        else:
            # foreign key comparison
            changed = old.pk != value.pk
    else:
        if old is None and value is not None:
            changed = True
        else:
            changed = text_type(old) != text_type(value)
    if changed:
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
            obj._dirty_fields = []
        # obj._is_dirty.append(u'[%s %s->%s]' % (fieldname, old, value))
        obj._dirty_fields.append(fieldname)


def update(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and  was saved.
    """
    for key, value in data.items():
        setfield(obj, key, value)
    if getattr(obj, '_is_dirty', None):
        logger.debug(u''.join(obj._is_dirty))
        obj.save(update_fields=obj._dirty_fields)
        del obj._is_dirty
        del obj._dirty_fields
        return True
