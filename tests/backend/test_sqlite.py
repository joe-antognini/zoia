import tempfile
import unittest
from pathlib import Path

from ..context import zoia
import zoia.backend.config
import zoia.backend.sqlite


class TestEntry(unittest.TestCase):
    def test_to_dict(self):
        authors = [
            zoia.backend.sqlite.Author(
                first_name='John',
                last_name='Doe',
            ),
            zoia.backend.sqlite.Author(
                first_name='Jane',
                last_name='Roe',
            ),
        ]
        entry = zoia.backend.sqlite.Entry(
            citekey='doe+roe01-foo',
            entry_type='article',
            title='Foo',
            year=2001,
            arxiv_id='2001.00001',
            authors=authors,
            other_metadata='{"journal": "qux"}',
        )

        observed_dict = entry.to_dict()

        expected_dict = {
            'citekey': 'doe+roe01-foo',
            'entry_type': 'article',
            'title': 'Foo',
            'year': 2001,
            'arxiv_id': '2001.00001',
            'authors': [['John', 'Doe'], ['Jane', 'Roe']],
            'journal': 'qux',
            'tags': [],
        }

        self.assertEqual(observed_dict, expected_dict)

    def test_from_dict(self):
        input_dictionary = {
            'entry_type': 'article',
            'title': 'Foo',
            'year': 2001,
            'arxiv_id': '2001.00001',
            'authors': [['John', 'Doe'], ['Jane', 'Roe']],
            'journal': 'qux',
        }

        entry = zoia.backend.sqlite.Entry.from_dict(
            'doe+roe01-foo', input_dictionary
        )

        self.assertEqual(entry.citekey, 'doe+roe01-foo')
        self.assertEqual(entry.year, 2001)
        self.assertEqual(entry.title, 'Foo')
        self.assertEqual(entry.authors[0].first_name, 'John')
        self.assertEqual(entry.authors[1].last_name, 'Roe')


class TestSqlLiteMetadata(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        library_root = Path(self.tmpdir.name) / 'library'
        db_root = Path(self.tmpdir.name) / 'data'

        library_root.mkdir()
        db_root.mkdir()

        self.config = zoia.backend.config.ZoiaConfig(
            library_root=str(library_root),
            db_root=str(db_root),
            backend=zoia.backend.config.ZoiaBackend.SQLITE,
        )

        authors = [
            zoia.backend.sqlite.Author(
                first_name='John',
                last_name='Doe',
            ),
            zoia.backend.sqlite.Author(
                first_name='Jane',
                last_name='Roe',
            ),
        ]
        self.entry = zoia.backend.sqlite.Entry(
            citekey='doe+roe01-foo',
            entry_type='article',
            title='Foo',
            year=2001,
            arxiv_id='2001.00001',
            isbn='9780691159027',
            doi='10.1000/foo',
            pdf_md5='foobar',
            authors=authors,
            other_metadata='{"journal": "qux"}',
        )

    def _init_db(self):
        self.metadata = zoia.backend.sqlite.SQLiteMetadata(self.config)
        self.metadata.session.add(self.entry)
        self.metadata.session.commit()

    def test___init__(self):
        self._init_db()

        db_file = (
            Path(self.config.db_root)
            / zoia.backend.sqlite.ZOIA_METADATA_FILENAME
        )
        self.assertTrue(db_file.exists())

    def test____contains__(self):
        self._init_db()
        self.assertIn('doe+roe01-foo', self.metadata)
        self.assertNotIn('doe+roe02-bar', self.metadata)

    def test____getitem__(self):
        self._init_db()

        entry = self.metadata['doe+roe01-foo']
        expected_dict = {
            'citekey': 'doe+roe01-foo',
            'entry_type': 'article',
            'title': 'Foo',
            'year': 2001,
            'arxiv_id': '2001.00001',
            'isbn': '9780691159027',
            'doi': '10.1000/foo',
            'pdf_md5': 'foobar',
            'authors': [['John', 'Doe'], ['Jane', 'Roe']],
            'journal': 'qux',
            'tags': [],
        }
        self.assertEqual(entry, expected_dict)

    def test_replace(self):
        self._init_db()
        old_journal = self.metadata['doe+roe01-foo']['journal']
        self.assertNotEqual(old_journal, 'quux')
        new_entry = {
            'citekey': 'doe+roe01-foo',
            'entry_type': 'article',
            'title': 'Foo',
            'year': 2001,
            'arxiv_id': '2001.00001',
            'authors': [['John', 'Doe'], ['Jane', 'Roe']],
            'journal': 'quux',
        }
        self.metadata.replace('doe+roe01-foo', new_entry)
        new_journal = self.metadata['doe+roe01-foo']['journal']
        self.assertEqual(new_journal, 'quux')

    def test_rename_key(self):
        self._init_db()
        self.assertIn('doe+roe01-foo', self.metadata)
        self.assertNotIn('doe+roe02-bar', self.metadata)
        self.metadata.rename_key('doe+roe01-foo', 'doe+roe02-bar')

        self.assertNotIn('doe+roe01-foo', self.metadata)
        self.assertIn('doe+roe02-bar', self.metadata)
        self.assertEqual(self.metadata['doe+roe02-bar']['title'], 'Foo')

    def test_arxiv_id_exists(self):
        self._init_db()
        self.assertTrue(self.metadata.arxiv_id_exists('2001.00001'))
        self.assertFalse(self.metadata.arxiv_id_exists('2001.00002'))

    def test_isbn_exists(self):
        self._init_db()
        self.assertTrue(self.metadata.isbn_exists('9780691159027'))
        self.assertFalse(self.metadata.isbn_exists('1'))

    def test_doi_exists(self):
        self._init_db()
        self.assertTrue(self.metadata.doi_exists('10.1000/foo'))
        self.assertFalse(self.metadata.doi_exists('10.1000/bar'))

    def test_pdf_md5_hash_exists(self):
        self._init_db()
        self.assertTrue(self.metadata.pdf_md5_hash_exists('foobar'))
        self.assertFalse(self.metadata.pdf_md5_hash_exists('bazqux'))
