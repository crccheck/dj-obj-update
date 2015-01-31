from django.test import TestCase

from dummy.models import Foo


class RenamemeTest(TestCase):
    def test_tests_run(self):
        self.assertEqual(Foo.objects.count(), 0)
