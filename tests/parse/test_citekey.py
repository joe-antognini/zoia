import unittest
import unittest.mock

from ..context import zoia
import zoia.parse.citekey
import zoia.backend.metadata
from ..fixtures.metadata import ZoiaUnitTest


class TestHelpers(unittest.TestCase):
    def test__get_title_start(self):
        self.assertEqual(
            zoia.parse.citekey._get_title_start(
                'Can quantum-mechanical description of physical reality be '
                'considered complete'
            ),
            'can',
        )

        self.assertEqual(
            zoia.parse.citekey._get_title_start(
                'On the electrodynamics of moving bodies'
            ),
            'electrodynamics',
        )

    def test__apply_citekey_format(self):
        citekey = zoia.parse.citekey._apply_citekey_format(
            name_string='Doe',
            year=99,
            first_word_of_title='foo',
            identifier=None,
        )
        self.assertEqual(citekey, 'doe99-foo')

        citekey = zoia.parse.citekey._apply_citekey_format(
            name_string='Doe',
            year=99,
            first_word_of_title='foo',
            identifier='a',
        )
        self.assertEqual(citekey, 'doe99a-foo')

    def test__generate_identifiers(self):
        for identifier in zoia.parse.citekey._generate_identifiers():
            self.assertEqual(identifier, 'b')
            break

        for i, identifier in enumerate(
            zoia.parse.citekey._generate_identifiers()
        ):
            if i == 0:
                self.assertEqual(identifier, 'b')
            elif i == 1:
                self.assertEqual(identifier, 'c')
            elif i == 24:
                self.assertEqual(identifier, 'z')
            elif i == 25:
                self.assertEqual(identifier, 'aa')
            elif i == 26:
                self.assertEqual(identifier, 'ab')
            elif i == 51:
                self.assertEqual(identifier, 'ba')
            elif i > 51:
                break


class TestCreateCitekey(ZoiaUnitTest):
    def test_create_citekey_one_author_no_collision(self):
        metadatum = zoia.backend.metadata.Metadatum(
            entry_type='article',
            title='The Foo Bar',
            authors=[['John', 'Doe']],
            year=1999,
        )

        citekey = zoia.parse.citekey.create_citekey(self.metadata, metadatum)
        self.assertEqual(citekey, 'doe99-foo')

    def test_create_citekey_one_author_with_collision(self):
        metadatum = zoia.backend.metadata.Metadatum(
            entry_type='article',
            title='The Foo Bar',
            authors=[['John', 'Doe']],
            year=1999,
        )

        self.metadata._metadata = {'doe99-foo': None}

        citekey = zoia.parse.citekey.create_citekey(self.metadata, metadatum)
        self.assertEqual(citekey, 'doe99b-foo')

    def test_create_citekey_two_authors_no_collision(self):
        metadatum = zoia.backend.metadata.Metadatum(
            entry_type='article',
            title='The Foo Bar',
            authors=[['John', 'Doe'], ['Jane', 'Roe']],
            year=1999,
        )

        citekey = zoia.parse.citekey.create_citekey(self.metadata, metadatum)
        self.assertEqual(citekey, 'doe+roe99-foo')

    def test_create_citekey_three_authors_no_collision(self):
        metadatum = zoia.backend.metadata.Metadatum(
            entry_type='article',
            title='The Foo Bar',
            authors=[['John', 'Doe'], ['Jane', 'Roe'], ['Joe', 'Bloggs']],
            year=1999,
        )

        citekey = zoia.parse.citekey.create_citekey(self.metadata, metadatum)
        self.assertEqual(citekey, 'doe+99-foo')
