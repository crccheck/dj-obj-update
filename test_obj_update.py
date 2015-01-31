from __future__ import unicode_literals

from django.test import TestCase

from dummy.models import Foo

from obj_update import update


class RenamemeTest(TestCase):
    def test_can_update_fields(self):
        # setup
        new_val = 'hello2'
        foo = Foo.objects.create(text='hello')

        with self.assertNumQueries(1):
            update(foo, {'text': 'hello2'})
        self.assertEqual(Foo.objects.get(pk=foo.pk).text, new_val)

    def test_no_changes_mean_no_queries(self):
        # setup
        foo = Foo.objects.create(text='hello')

        with self.assertNumQueries(0):
            update(foo, {'text': 'hello'})

        with self.assertNumQueries(0):
            update(foo, {'text': u'hello'})

        # FIXME?
        # with self.assertNumQueries(0):
        #     update(foo, {'text': b'hello'})
