import unittest

import zoia.backend.metadata


class TestMetadatum(unittest.TestCase):
    def test_metadatum_from_dict(self):
        d = {
            'entry_type': 'article',
            'title': 'foo',
            'authors': ['John Doe', 'Jane Roe'],
            'year': 2001,
        }
        metadatum = zoia.backend.metadata.Metadatum.from_dict(d)
        self.assertEqual(metadatum.title, 'foo')
        self.assertEqual(metadatum.authors, [['John', 'Doe'], ['Jane', 'Roe']])
        self.assertEqual(metadatum.year, 2001)

    def test_metadatum_to_dict(self):
        metadatum = zoia.backend.metadata.Metadatum(
            entry_type='article',
            title='Foo',
            authors=['John Doe', 'Jane Roe'],
            year=2001,
        )

        d = metadatum.to_dict()

        expected_dict = {
            'entry_type': 'article',
            'title': 'Foo',
            'authors': [['John', 'Doe'], ['Jane', 'Roe']],
            'year': 2001,
            'tags': [],
        }
        self.assertEqual(d, expected_dict)

    def test_metadatum_str(self):
        metadatum = zoia.backend.metadata.Metadatum(
            entry_type='article',
            title='Foo',
            authors=['John Doe', 'Jane Roe'],
            year=2001,
        )

        self.assertEqual(str(metadatum), 'Doe & Roe (2001), "Foo"')
