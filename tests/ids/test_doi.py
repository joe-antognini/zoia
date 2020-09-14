import unittest

from ..context import zoia
import zoia.ids.doi


class TestDoi(unittest.TestCase):
    def test_is_doi(self):
        self.assertFalse(zoia.ids.doi.is_doi('foo'))
        self.assertFalse(zoia.ids.doi.is_doi('11.23915/distill.00005'))
        self.assertFalse(zoia.ids.doi.is_doi('10.1/distill.00005'))
        self.assertFalse(zoia.ids.doi.is_doi('10.23915'))
        self.assertFalse(zoia.ids.doi.is_doi('10.23915/'))
        self.assertTrue(zoia.ids.doi.is_doi('10.23915/distill.00005'))
