import unittest

from .context import zoia
import zoia.normalization


class TestNormalization(unittest.TestCase):
    def test_strip_diacritics(self):
        self.assertEqual(zoia.normalization.strip_diacritics('foo'), 'foo')
        self.assertEqual(zoia.normalization.strip_diacritics('Foo'), 'Foo')
        self.assertEqual(zoia.normalization.strip_diacritics('Fóò'), 'Foo')

    def test_normalize_string(self):
        self.assertEqual(zoia.normalization.normalize_name('foo'), 'foo')
        self.assertEqual(zoia.normalization.normalize_name('Foo'), 'foo')
        self.assertEqual(zoia.normalization.normalize_name('Fóò'), 'foo')

    def test_split_name(self):
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

    def test_normalize_title_word(self):
        self.assertEqual(zoia.normalization.normalize_title_word('The'), 'the')
        self.assertEqual(
            zoia.normalization.normalize_title_word('"Why"'), 'why'
        )
        self.assertEqual(
            zoia.normalization.normalize_title_word(r'$\eta_3$'), 'eta3'
        )
