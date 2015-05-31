Django Object Update
====================

.. image:: https://travis-ci.org/crccheck/dj-obj-update.svg?branch=master
    :target: https://travis-ci.org/crccheck/dj-obj-update

``dj-obj-update`` is a module that helps you do two things while updating an
object:

1. Only do a save if something changed
2. Log what changed (the logger name is ``obj_update`` and only outputs DEBUG)


Installation
------------

::

    pip install dj-obj-update


Usage
-----

Updating an object::

    from obj_update import obj_update

    new_data = {
        'flavor': 'chocolate',
    }
    for obj in queryset:
        obj_update(obj, new_data)


Replacement for ``update_or_create``::

    from obj_update import obj_update_or_create

    choice, created = obj_update_or_create(
        Choice,
        question=question,
        defaults={'choice_text': 'Flour or corn?'},
    )

https://docs.djangoproject.com/en/1.8/ref/models/querysets/#update-or-create
