import unittest

from .context import zoia
import zoia.normalization


class TestNormalization(unittest.TestCase):
    def test__strip_diacritics(self):
        self.assertEqual(zoia.normalization.strip_diacritics('foo'), 'foo')
        self.assertEqual(zoia.normalization.strip_diacritics('Foo'), 'Foo')
        self.assertEqual(zoia.normalization.strip_diacritics('Fóò'), 'Foo')

    def test__normalize_string(self):
        self.assertEqual(zoia.normalization.normalize_string('foo'), 'foo')
        self.assertEqual(zoia.normalization.normalize_string('Foo'), 'foo')
        self.assertEqual(zoia.normalization.normalize_string('Fóò'), 'foo')

    def test__split_name(self):
        self.assertEqual(zoia.normalization.split_name('Doe'), ['', 'Doe'])
        self.assertEqual(
            zoia.normalization.split_name('John Doe'), ['John', 'Doe']
        )
        self.assertEqual(
            zoia.normalization.split_name('John van Doe'), ['John', 'van Doe']
        )
        self.assertEqual(
            zoia.normalization.split_name('John Q. Public'),
            ['John Q.', 'Public'],
        )
