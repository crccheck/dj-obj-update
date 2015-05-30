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

::

    from obj_update import update

    new_data = {
        'flavor': 'chocolate',
    }
    for obj in queryset:
        update(obj, new_data)
