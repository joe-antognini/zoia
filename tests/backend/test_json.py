import tempfile
import unittest
import unittest.mock
from pathlib import Path

from ..context import zoia
import zoia.backend.config
import zoia.backend.json
from ..fixtures.metadata import ZoiaUnitTest


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmpdir.name)

        library_root = self.tmpdir / 'library'
        db_root = self.tmpdir / 'metadata'

        library_root.mkdir()
        db_root.mkdir()

        self.zoia_config = zoia.backend.config.ZoiaConfig(
            library_root=str(library_root),
            db_root=str(db_root),
            backend=zoia.backend.config.ZoiaBackend.JSON,
        )

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_metadata_init(self):
        metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata._metadata, {})

    def test_write_load_metadata(self):
        old_metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        old_metadata._metadata = {'foo': 'bar'}
        old_metadata.write()

        new_metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        self.assertEqual(old_metadata._metadata, new_metadata._metadata)

    def test___contains__(self):
        metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        metadata._metadata = {'foo': 'bar'}
        self.assertIn('foo', metadata)
        self.assertNotIn('baz', metadata)

    def test___getitem__(self):
        metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        metadata._metadata = {'foo': 'bar'}
        self.assertEqual(metadata['foo'], 'bar')

    def test___setitem__(self):
        metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        metadata._metadata = {'foo': 'bar'}
        metadata['baz'] = 'qux'
        self.assertEqual(metadata._metadata, {'foo': 'bar', 'baz': 'qux'})

    def test_rename_key(self):
        metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        metadata._metadata = {'foo': 'bar', 'baz': 'qux'}

        metadata.rename_key('foo', 'quux')
        self.assertEqual(metadata._metadata, {'quux': 'bar', 'baz': 'qux'})

    def test_rename_key_existing_key(self):
        metadata = zoia.backend.json.JSONMetadata(self.zoia_config)
        metadata._metadata = {'foo': 'bar', 'baz': 'qux'}
        with self.assertRaises(KeyError):
            metadata.rename_key('quuz', 'foo')

        with self.assertRaises(KeyError):
            metadata.rename_key('foo', 'baz')


class TestMetadataGetters(ZoiaUnitTest):
    def setUp(self):
        super().setUp()
        self.metadata._metadata = {
            'doe09-foo': {'arxiv_id': '0901.0123'},
            'johnson13-qux': {'doi': '10.1000/foo'},
            'roe19-baz': {'isbn': '9781499999990'},
            'smith10-bar': {'arxiv_id': '1002.1001'},
            'thompson11-quux': {'pdf_md5': '2aa5d113c95b2432dbdb7c6440115774'},
        }

    def test_get_arxiv_ids(self):
        self.assertTrue(self.metadata.arxiv_id_exists('0901.0123'))
        self.assertFalse(self.metadata.arxiv_id_exists('0901.0124'))

    def test_get_isbns(self):
        self.assertTrue(self.metadata.isbn_exists('9781499999990'))
        self.assertFalse(self.metadata.isbn_exists('9781499999991'))

    def test_get_dois(self):
        self.assertTrue(self.metadata.doi_exists('10.1000/foo'))
        self.assertFalse(self.metadata.doi_exists('10.1000/bar'))

    def test_get_pdf_md5_hashes(self):
        self.assertTrue(
            self.metadata.pdf_md5_hash_exists(
                '2aa5d113c95b2432dbdb7c6440115774'
            )
        )
        self.assertFalse(self.metadata.pdf_md5_hash_exists('foo'))
