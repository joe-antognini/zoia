import unittest

from .context import zoia
import zoia.citekey


class TestHelpesr(unittest.TestCase):
    def test__strip_diacritics(self):
        self.assertEqual(zoia.citekey._strip_diacritics('foo'), 'foo')
        self.assertEqual(zoia.citekey._strip_diacritics('Foo'), 'Foo')
        self.assertEqual(zoia.citekey._strip_diacritics('Fóò'), 'Foo')

    def test__normalize_string(self):
        self.assertEqual(zoia.citekey._normalize_string('foo'), 'foo')
        self.assertEqual(zoia.citekey._normalize_string('Foo'), 'foo')
        self.assertEqual(zoia.citekey._normalize_string('Fóò'), 'foo')

    def test__get_last_name(self):
        self.assertEqual(zoia.citekey._get_last_name('Doe'), ['Doe'])
        self.assertEqual(zoia.citekey._get_last_name('John Doe'), ['Doe'])
        self.assertEqual(
            zoia.citekey._get_last_name('John van Doe'), ['van', 'Doe']
        )
        self.assertEqual(
            zoia.citekey._get_last_name('John Q. Public'), ['Public']
        )

    def test__get_title_start(self):
        self.assertEqual(
            zoia.citekey._get_title_start(
                'Can quantum-mechanical description of physical reality be '
                'considered complete'
            ),
            'can',
        )

        self.assertEqual(
            zoia.citekey._get_title_start(
                'On the electrodynamics of moving bodies'
            ),
            'electrodynamics',
        )
