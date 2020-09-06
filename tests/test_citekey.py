import unittest
import unittest.mock

from .context import zoia
import zoia.citekey
import zoia.metadata


class TestHelpers(unittest.TestCase):
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

    def test__apply_citekey_format(self):
        citekey = zoia.citekey._apply_citekey_format(
            name_string='Doe',
            year=99,
            first_word_of_title='foo',
            identifier=None,
        )
        self.assertEqual(citekey, 'doe99-foo')

        citekey = zoia.citekey._apply_citekey_format(
            name_string='Doe',
            year=99,
            first_word_of_title='foo',
            identifier='a',
        )
        self.assertEqual(citekey, 'doe99a-foo')

    def test__generate_identifiers(self):
        for identifier in zoia.citekey._generate_identifiers():
            self.assertEqual(identifier, 'b')
            break

        for i, identifier in enumerate(zoia.citekey._generate_identifiers()):
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


class TestCreateCitekey(unittest.TestCase):
    @unittest.mock.patch('zoia.citekey.zoia.metadata.load_metadata')
    def test_create_citekey_one_author_no_collision(self, mock_load_metadata):
        metadatum = zoia.metadata.Metadatum(
            title='The Foo Bar', authors=[['John', 'Doe']], year=1999
        )

        mock_load_metadata.return_value = {'doe00-baz': None}
        citekey = zoia.citekey.create_citekey(metadatum)
        self.assertEqual(citekey, 'doe99-foo')

    @unittest.mock.patch('zoia.citekey.zoia.metadata.load_metadata')
    def test_create_citekey_one_author_with_collision(
        self, mock_load_metadata
    ):
        metadatum = zoia.metadata.Metadatum(
            title='The Foo Bar', authors=[['John', 'Doe']], year=1999
        )

        mock_load_metadata.return_value = {'doe99-foo': None}
        citekey = zoia.citekey.create_citekey(metadatum)
        self.assertEqual(citekey, 'doe99b-foo')
