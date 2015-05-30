from __future__ import unicode_literals

import datetime

from django.test import TestCase

from dummy.models import FooModel, BarModel

from obj_update import update, text_type


class RenamemeTest(TestCase):
    def test_can_update_fields(self):
        # setup
        new_val = 'hello2'
        foo = FooModel.objects.create(text='hello')

        with self.assertNumQueries(1):
            update(foo, {'text': 'hello2'})
        self.assertEqual(FooModel.objects.get(pk=foo.pk).text, new_val)

    def test_no_changes_mean_no_queries(self):
        # setup
        foo = FooModel.objects.create(text='hello')

        with self.assertNumQueries(0):
            update(foo, {'text': 'hello'})

        with self.assertNumQueries(0):
            update(foo, {'text': u'hello'})

        # FIXME?
        # with self.assertNumQueries(0):
        #     update(foo, {'text': b'hello'})

    #####################
    # MODEL FIELD TYPES #
    #####################

    def test_datetime_init_as_str(self):
        # setup
        foo = FooModel.objects.create(datetime='2029-09-20 01:02:03')
        # sanity check
        self.assertIsInstance(foo.datetime, text_type)

        with self.assertNumQueries(0):
            # 0 because input is exactly the same
            update(foo, {'datetime': '2029-09-20 01:02:03'})

        with self.assertNumQueries(0):
            # 0 because input is python type that reprs the same
            update(foo, {'datetime': datetime.datetime(2029, 9, 20, 1, 2, 3)})

        with self.assertNumQueries(1):
            # 1 because input looks close, but not quite close enough
            update(foo, {'datetime': '2029-09-20T01:02:03'})

    def test_datetime_init_as_datetime(self):
        # setup
        foo = FooModel.objects.create(datetime=datetime.datetime(2029, 9, 20, 1, 2, 3))
        # sanity check
        self.assertIsInstance(foo.datetime, datetime.datetime)

        with self.assertNumQueries(0):
            # 0 because input is exactly the same
            update(foo, {'datetime': datetime.datetime(2029, 9, 20, 1, 2, 3)})

        with self.assertNumQueries(0):
            # 0 because input is python type that reprs the same
            update(foo, {'datetime': '2029-09-20 01:02:03'})

        with self.assertNumQueries(1):
            update(foo, {'datetime': datetime.datetime(1111, 1, 1, 1, 1, 1)})

    def test_decimal_a_text(self):
        # setup
        foo = FooModel.objects.create(decimal='10.1')
        # sanity check
        self.assertIsInstance(foo.decimal, text_type)

        with self.assertNumQueries(0):
            # 0 because input is exactly the same
            update(foo, {'decimal': '10.1'})

        with self.assertNumQueries(0):
            update(foo, {'decimal': 10.1})

        with self.assertNumQueries(1):
            update(foo, {'decimal': 1.01})

    # is this any different from text?
    def test_slug(self):
        # setup
        foo = FooModel.objects.create(slug='hello')

        with self.assertNumQueries(0):
            update(foo, {'slug': 'hello'})

        with self.assertNumQueries(1):
            update(foo, {'slug': 'hello1'})

    def test_text(self):
        # setup
        foo = FooModel.objects.create(text='hello')

        with self.assertNumQueries(0):
            update(foo, {'text': 'hello'})

        with self.assertNumQueries(1):
            update(foo, {'text': 'hello1'})

    def test_foreignkey_adding(self):
        # setup
        bar = BarModel.objects.create()
        foo = FooModel.objects.create(text='hello')

        with self.assertNumQueries(0):
            update(foo, {'foreignkey': None})

        with self.assertNumQueries(1):
            update(foo, {'foreignkey': bar})

    def test_foreignkey_removing(self):
        # setup
        bar = BarModel.objects.create()
        foo = FooModel.objects.create(text='hello', foreignkey=bar)

        with self.assertNumQueries(0):
            update(foo, {'foreignkey': bar})

        with self.assertNumQueries(1):
            update(foo, {'foreignkey': None})

    def test_foreignkey_changing(self):
        # setup
        bar1 = BarModel.objects.create()
        bar2 = BarModel.objects.create()
        foo = FooModel.objects.create(text='hello', foreignkey=bar1)

        with self.assertNumQueries(0):
            update(foo, {'foreignkey': bar1})

        with self.assertNumQueries(1):
            update(foo, {'foreignkey': bar2})
