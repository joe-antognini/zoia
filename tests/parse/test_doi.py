import unittest

from ..context import zoia
import zoia.parse.doi


class TestDoi(unittest.TestCase):
    def test_is_doi(self):
        self.assertFalse(zoia.parse.doi.is_doi('foo'))
        self.assertFalse(zoia.parse.doi.is_doi('11.23915/distill.00005'))
        self.assertFalse(zoia.parse.doi.is_doi('10.1/distill.00005'))
        self.assertFalse(zoia.parse.doi.is_doi('10.23915'))
        self.assertFalse(zoia.parse.doi.is_doi('10.23915/'))
        self.assertTrue(zoia.parse.doi.is_doi('10.23915/distill.00005'))
        self.assertTrue(zoia.parse.doi.is_doi('doi:10.23915/distill.00005'))

    def test_normalize(self):
        self.assertEqual(
            zoia.parse.doi.normalize('10.23915/distill.00005'),
            '10.23915/distill.00005',
        )

        self.assertEqual(
            zoia.parse.doi.normalize('doi:10.23915/distill.00005'),
            '10.23915/distill.00005',
        )

        self.assertEqual(
            zoia.parse.doi.normalize('http://doi.org/10.23915/distill.00005'),
            '10.23915/distill.00005',
        )

        self.assertEqual(
            zoia.parse.doi.normalize(
                'https://dx.doi.org/10.23915/distill.00005'
            ),
            '10.23915/distill.00005',
        )

        self.assertEqual(
            zoia.parse.doi.normalize(
                'https://arxiv.org/10.23915/distill.00005'
            ),
            'https://arxiv.org/10.23915/distill.00005',
        )
