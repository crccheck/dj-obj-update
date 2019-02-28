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

Updating an object
''''''''''''''''''

::

    from obj_update import obj_update

    new_data = {
        'flavor': 'chocolate',
    }
    for obj in queryset:
        obj_update(obj, new_data)

Dry run updating an object
''''''''''''''''''''''''''

::

    from obj_update import obj_update

    logger.setLevel(logging.DEBUG)  # see "Logging changes" below

    new_data = {
        'flavor': 'chocolate',
    }
    for obj in queryset:
        obj_update(obj, new_data, save=False)

Replacement for ``update_or_create``
''''''''''''''''''''''''''''''''''''

::

    from obj_update import obj_update_or_create

    choice, created = obj_update_or_create(
        Choice,
        question=question,
        defaults={'choice_text': 'Flour or corn?'},
    )

https://docs.djangoproject.com/en/2.0/ref/models/querysets/#update-or-create

Dealing with ``auto_now`` fields
''''''''''''''''''''''''''''''''

By default, ``dj-obj-update`` constructs an ``update_fields`` when it saves.
This means fields like the primary key, ``auto_now``, and ``auto_now_add``
might not get saved. If you need this, you can set ``update_fields=None``.
Usage is the same as Django's:

https://docs.djangoproject.com/en/2.1/ref/models/instances/#specifying-which-fields-to-save

Logging changes
'''''''''''''''

Using ``python-json-logger``::

    import logging
    from pythonjsonlogger.jsonlogger import JsonFormatter

    logger = logging.getLogger('obj_update')
    handler = logging.FileHandler('log/my_obj_changes.log')
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

With JSON logging, you'll get messages like::

    {"message": "[text hello->hello2]", "model": "FooModel", "pk": 1, "changes": {"text": {"old": "hello", "new": "hello2"}}}

With a normal logger, you'll still get output, but it won't have as much information::

    [text hello->hello2]
