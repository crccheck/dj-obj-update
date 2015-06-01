from __future__ import unicode_literals

from decimal import Decimal
from StringIO import StringIO
import datetime
import json
import logging

from django.test import TestCase, TransactionTestCase
from pythonjsonlogger.jsonlogger import JsonFormatter

from dummy.models import FooModel, BarModel

from obj_update import obj_update, obj_update_or_create, text_type


class UpdateTests(TestCase):
    def test_can_update_fields(self):
        foo = FooModel.objects.create(text='hello')

        with self.assertNumQueries(1):
            obj_update(foo, {'text': 'hello2'})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.text, 'hello2')

    def test_no_changes_mean_no_queries(self):
        # setup
        foo = FooModel.objects.create(text='hello')

        with self.assertNumQueries(0):
            obj_update(foo, {'text': 'hello'})

        with self.assertNumQueries(0):
            obj_update(foo, {'text': u'hello'})

        # FIXME? This fails in Python 3
        # with self.assertNumQueries(0):
        #     obj_update(foo, {'text': b'hello'})

    # LOGGING
    #########

    def test_logging(self):
        logger = logging.getLogger('obj_update')
        log_output = StringIO()
        handler = logging.StreamHandler(stream=log_output)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        foo = FooModel.objects.create(text='hello')

        obj_update(foo, {'text': 'hello2'})

        log_output.seek(0)
        logged_lines = log_output.readlines()
        message_logged = json.loads(logged_lines[0])
        self.assertEqual(
            message_logged['obj_update']['model'], 'FooModel')
        self.assertEqual(
            message_logged['obj_update']['pk'], foo.pk)
        self.assertEqual(
            message_logged['obj_update']['changes']['text']['old'], 'hello')
        self.assertEqual(
            message_logged['obj_update']['changes']['text']['new'], 'hello2')

        # HACK too lazy to remove the handler, this just silences it
        logger.setLevel(logging.WARNING)

    # MODEL FIELD TYPES
    ###################

    def test_datetime_init_as_str(self):
        # setup
        foo = FooModel.objects.create(datetime='2029-09-20 01:02:03')
        # sanity check
        self.assertIsInstance(foo.datetime, text_type)

        with self.assertNumQueries(0):
            # 0 because input is exactly the same
            obj_update(foo, {'datetime': '2029-09-20 01:02:03'})

        with self.assertNumQueries(0):
            # 0 because input is python type that reprs the same
            obj_update(foo, {'datetime': datetime.datetime(2029, 9, 20, 1, 2, 3)})

        with self.assertNumQueries(1):
            # 1 because input looks close, but not quite close enough
            obj_update(foo, {'datetime': '2029-09-20T01:02:03'})

    def test_datetime_init_as_datetime(self):
        # setup
        foo = FooModel.objects.create(datetime=datetime.datetime(2029, 9, 20, 1, 2, 3))
        # sanity check
        self.assertIsInstance(foo.datetime, datetime.datetime)

        with self.assertNumQueries(0):
            # 0 because input is exactly the same
            obj_update(foo, {'datetime': datetime.datetime(2029, 9, 20, 1, 2, 3)})

        with self.assertNumQueries(0):
            # 0 because input is python type that reprs the same
            obj_update(foo, {'datetime': '2029-09-20 01:02:03'})

        with self.assertNumQueries(1):
            obj_update(foo, {'datetime': datetime.datetime(1111, 1, 1, 1, 1, 1)})

    def test_decimal_a_text(self):
        # setup
        foo = FooModel.objects.create(decimal='10.1')
        # sanity check
        self.assertIsInstance(foo.decimal, text_type)

        with self.assertNumQueries(0):
            # 0 because input is exactly the same
            obj_update(foo, {'decimal': '10.1'})

        with self.assertNumQueries(0):
            obj_update(foo, {'decimal': 10.1})

        with self.assertNumQueries(1):
            obj_update(foo, {'decimal': 1.01})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.decimal, Decimal('1.01'))

    # is this any different from text?
    def test_slug(self):
        # setup
        foo = FooModel.objects.create(slug='hello')

        with self.assertNumQueries(0):
            obj_update(foo, {'slug': 'hello'})

        with self.assertNumQueries(1):
            obj_update(foo, {'slug': 'hello1'})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.slug, 'hello1')

    def test_text(self):
        # setup
        foo = FooModel.objects.create(text='hello')

        with self.assertNumQueries(0):
            obj_update(foo, {'text': 'hello'})

        with self.assertNumQueries(1):
            obj_update(foo, {'text': 'hello1'})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.text, 'hello1')

    def test_foreignkey_adding(self):
        foo = FooModel.objects.create(foreignkey=None)
        bar = BarModel.objects.create()

        with self.assertNumQueries(0):
            obj_update(foo, {'foreignkey': None})

        with self.assertNumQueries(1):
            obj_update(foo, {'foreignkey': bar})

    def test_foreignkey_removing(self):
        # setup
        bar = BarModel.objects.create()
        foo = FooModel.objects.create(foreignkey=bar)

        with self.assertNumQueries(0):
            obj_update(foo, {'foreignkey': bar})
        self.assertEqual(foo.foreignkey, bar)

        with self.assertNumQueries(1):
            obj_update(foo, {'foreignkey': None})

        foo = FooModel.objects.get(pk=foo.pk)
        self.assertEqual(foo.foreignkey, None)

    def test_foreignkey_changing(self):
        # setup
        bar1 = BarModel.objects.create()
        bar2 = BarModel.objects.create()
        foo = FooModel.objects.create(text='hello', foreignkey=bar1)

        with self.assertNumQueries(0):
            obj_update(foo, {'foreignkey': bar1})
        self.assertEqual(foo.foreignkey, bar1)

        with self.assertNumQueries(1):
            obj_update(foo, {'foreignkey': bar2})
        self.assertEqual(foo.foreignkey, bar2)


class ObjUpdateOrCreateTests(TransactionTestCase):
    def test_workflow(self):
        # Test creation
        with self.assertNumQueries(3):
            # 1. SELECT
            # 2. BEGIN
            # 3. INSERT
            foo, created = obj_update_or_create(FooModel, text='hi', defaults={
                'slug': 'leopard',
            })
        self.assertTrue(created)
        self.assertEqual(foo.text, 'hi')
        self.assertEqual(foo.slug, 'leopard')

        # Test updating with nothing new
        with self.assertNumQueries(1):
            # 1. SELECT
            foo, created = obj_update_or_create(FooModel, text='hi', defaults={
                'slug': 'leopard',
            })
        self.assertFalse(created)
        self.assertEqual(foo.text, 'hi')
        self.assertEqual(foo.slug, 'leopard')

        # Test updating with new data
        with self.assertNumQueries(3):
            # 1. SELECT
            # 2. BEGIN
            # 3. INSERT
            foo, created = obj_update_or_create(FooModel, text='hi', defaults={
                'slug': 'lemon', 'decimal': '0.01',
            })
        self.assertFalse(created)
        self.assertEqual(foo.text, 'hi')
        self.assertEqual(foo.slug, 'lemon')
        self.assertEqual(foo.decimal, '0.01')
