import datetime as dt
import json
import logging.config
import sys
import unittest
import os
from decimal import Decimal
from io import StringIO
from unittest import skipIf

import django
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from pythonjsonlogger.jsonlogger import JsonFormatter

from test_app.models import FooModel, BarModel

from obj_update import obj_update, obj_update_or_create

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "json"},
            "null": {"class": "logging.NullHandler", "formatter": "json"},
        },
        "loggers": {
            # Edit this config to play with these to test different logging scenarios
            "obj_update": {"level": "DEBUG", "handlers": ["null"]},
            # "obj_update.create": {"level": "DEBUG", "handlers": ["console"]},
            # "obj_update.update": {"level": "DEBUG", "handlers": ["console"]},
        },
    }
)


class UpdateTests(TestCase):
    def test_can_update_fields(self):
        foo = FooModel.objects.create(text="hello")

        with self.assertNumQueries(1):
            obj_update(foo, {"text": "hello2"})

        foo.refresh_from_db()
        self.assertEqual(foo.text, "hello2")

    def test_can_update_fields_but_not_save(self):
        foo = FooModel.objects.create(text="hello")

        with self.assertNumQueries(0):
            obj_update(foo, {"text": "hello2"}, update_fields=[])

        self.assertEqual(foo.text, "hello2")

    def test_can_update_fields_but_not_save_DEPRECATED(self):
        foo = FooModel.objects.create(text="hello")

        with self.assertNumQueries(0):
            obj_update(foo, {"text": "hello2"}, save=False)

        self.assertEqual(foo.text, "hello2")

    def test_update_fields_stuff(self):
        foo = FooModel(text="hello")
        # Sanity check: fails without update_fields
        with transaction.atomic(), self.assertRaises(ValueError):
            obj_update(foo, {"text": "hello2"})

        with self.assertNumQueries(1):
            obj_update(foo, {"text": "hello2"}, update_fields=None)

        foo.refresh_from_db()
        self.assertEqual(foo.text, "hello2")
        self.assertTrue(foo.id)

    def test_no_changes_mean_no_queries(self):
        # setup
        foo = FooModel.objects.create(text="hello")

        with self.assertNumQueries(0):
            obj_update(foo, {"text": "hello"})

        with self.assertNumQueries(0):
            obj_update(foo, {"text": u"hello"})

        # FIXME? This fails in Python 3
        # with self.assertNumQueries(0):
        #     obj_update(foo, {'text': b'hello'})

    # LOGGING
    #########

    @unittest.skipIf(sys.version_info < (3, 4, 0), 'Requires Python 3.4 or greater')
    def test_logging(self):
        foo = FooModel.objects.create(text="hello")

        with self.assertLogs("obj_update", level="DEBUG") as cm:
            obj_update(foo, {"text": "hello2"})

        self.assertEqual(len(cm.records), 1)
        record = cm.records[0]
        self.assertEqual(record.model, "FooModel")
        self.assertEqual(record.pk, foo.pk)
        self.assertEqual(record.changes["text"]["old"], "hello")
        self.assertEqual(record.changes["text"]["new"], "hello2")

    # MODEL FIELD TYPES
    ###################

    def test_datetime_vs_datetime(self):
        foo = FooModel.objects.create(datetime=dt.datetime(2029, 9, 20, 1, 2, 3))
        with self.assertNumQueries(0):
            obj_update(foo, {"datetime": dt.datetime(2029, 9, 20, 1, 2, 3)})

    def test_datetime_vs_str(self):
        foo = FooModel.objects.create(datetime=dt.datetime(2029, 9, 20, 1, 2, 3))
        with self.assertNumQueries(0):
            obj_update(foo, {"datetime": "2029-09-20 01:02:03"})

        with self.assertNumQueries(0):
            obj_update(foo, {"datetime": "2029-09-20T01:02:03"})

    def test_datetime_updates_str(self):
        foo = FooModel.objects.create(datetime=dt.datetime(2029, 9, 20, 1, 2, 3))
        with self.assertNumQueries(1):
            obj_update(foo, {"datetime": "2029-04-20 03:14:15"})

        with self.assertNumQueries(1):
            obj_update(foo, {"datetime": "2029-04-01T03:14:15"})

    def test_datetime_is_set(self):
        foo = FooModel.objects.create(datetime=dt.datetime(2029, 9, 20, 1, 2, 3))
        with self.assertNumQueries(1):
            obj_update(foo, {"datetime": dt.datetime(1111, 1, 1, 1, 1, 1)})

    def test_decimal_a_text(self):
        # setup
        foo = FooModel.objects.create(decimal="10.1")
        # sanity check
        self.assertIsInstance(foo.decimal, str)

        with self.assertNumQueries(0):
            # 0 because input is exactly the same
            obj_update(foo, {"decimal": "10.1"})

        with self.assertNumQueries(0):
            obj_update(foo, {"decimal": 10.1})

        with self.assertNumQueries(1):
            obj_update(foo, {"decimal": 1.01})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.decimal, Decimal("1.01"))

    # is this any different from text?
    def test_slug(self):
        # setup
        foo = FooModel.objects.create(slug="hello")

        with self.assertNumQueries(0):
            obj_update(foo, {"slug": "hello"})

        with self.assertNumQueries(1):
            obj_update(foo, {"slug": "hello1"})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.slug, "hello1")

    def test_text(self):
        # setup
        foo = FooModel.objects.create(text="hello")

        with self.assertNumQueries(0):
            obj_update(foo, {"text": "hello"})

        with self.assertNumQueries(1):
            obj_update(foo, {"text": "hello1"})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.text, "hello1")

    def test_foreignkey_adding(self):
        foo = FooModel.objects.create(foreignkey=None)
        bar = BarModel.objects.create()

        with self.assertNumQueries(0):
            obj_update(foo, {"foreignkey": None})

        with self.assertNumQueries(1):
            obj_update(foo, {"foreignkey": bar})

    def test_foreignkey_adding_as_id(self):
        foo = FooModel.objects.create(foreignkey=None)
        bar = BarModel.objects.create()

        with self.assertNumQueries(0):
            obj_update(foo, {"foreignkey": None})

        with self.assertNumQueries(1):
            obj_update(foo, {"foreignkey_id": bar.pk})
        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.foreignkey, bar)

    def test_foreignkey_removing(self):
        # setup
        bar = BarModel.objects.create()
        foo = FooModel.objects.create(foreignkey=bar)

        with self.assertNumQueries(0):
            obj_update(foo, {"foreignkey": bar})
        self.assertEqual(foo.foreignkey, bar)

        with self.assertNumQueries(1):
            obj_update(foo, {"foreignkey": None})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.foreignkey, None)

    def test_foreignkey_changing(self):
        # setup
        bar1 = BarModel.objects.create()
        bar2 = BarModel.objects.create()
        foo = FooModel.objects.create(text="hello", foreignkey=bar1)

        with self.assertNumQueries(0):
            obj_update(foo, {"foreignkey": bar1})
        self.assertEqual(foo.foreignkey, bar1)

        with self.assertNumQueries(1):
            obj_update(foo, {"foreignkey": bar2})
        self.assertEqual(foo.foreignkey, bar2)

    def test_foreignkey_changing_as_id(self):
        # setup
        bar1 = BarModel.objects.create()
        bar2 = BarModel.objects.create()
        foo = FooModel.objects.create(text="hello", foreignkey=bar1)

        with self.assertNumQueries(0):
            obj_update(foo, {"foreignkey_id": bar1.id})
        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.foreignkey, bar1)

        with self.assertNumQueries(1):
            obj_update(foo, {"foreignkey_id": bar2.id})
        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.foreignkey, bar2)


class ObjUpdateOrCreateTests(TransactionTestCase):
    def test_workflow(self):
        # Test creation
        with self.assertNumQueries(3):
            # 1. SELECT
            # 2. BEGIN
            # 3. INSERT
            foo, created = obj_update_or_create(
                FooModel, text="hi", defaults={"slug": "leopard"}
            )
        self.assertTrue(created)
        self.assertEqual(foo.text, "hi")
        self.assertEqual(foo.slug, "leopard")

        # Test updating with nothing new
        with self.assertNumQueries(1):
            # 1. SELECT
            foo, created = obj_update_or_create(
                FooModel, text="hi", defaults={"slug": "leopard"}
            )
        self.assertFalse(created)
        self.assertEqual(foo.text, "hi")
        self.assertEqual(foo.slug, "leopard")

        # Test updating with new data
        num_queries = 3 if django.VERSION < (2, 2) else 2
        with self.assertNumQueries(num_queries):
            # 1. SELECT
            # 2. BEGIN if Django<2.2  Django no longer always starts a transaction when a single query is being performed https://docs.djangoproject.com/en/2.2/releases/2.2/
            # 3. INSERT
            foo, created = obj_update_or_create(
                FooModel, text="hi", defaults={"slug": "lemon", "decimal": "0.01"}
            )
        self.assertFalse(created)
        self.assertEqual(foo.text, "hi")
        self.assertEqual(foo.slug, "lemon")
        self.assertEqual(foo.decimal, "0.01")
