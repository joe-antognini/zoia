import tempfile
import unittest
import unittest.mock
from pathlib import Path

from ..context import zoia
import zoia.backend.metadata


@unittest.mock.patch('zoia.backend.metadata.get_library_root')
class TestMetadata(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir.name

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_write_load_metadata(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.backend.metadata._write_metadata({'foo': 'bar'})
        metadata = zoia.backend.metadata.load_metadata()
        self.assertEqual(metadata, {'foo': 'bar'})

    def test_append_metadata(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.backend.metadata._write_metadata({'foo': 'bar'})
        zoia.backend.metadata.append_metadata('baz', 'qux')
        metadata = zoia.backend.metadata.load_metadata()
        self.assertEqual(metadata, {'foo': 'bar', 'baz': 'qux'})

    def test_initialize_metadata(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        self.assertFalse((Path(self.tmpdir) / '.metadata.json').exists())
        zoia.backend.metadata.initialize_metadata()
        self.assertTrue((Path(self.tmpdir) / '.metadata.json').exists())

    def test_initialize_metadata_already_existing(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        (Path(self.tmpdir) / '.metadata.json').touch()
        with self.assertRaises(RuntimeError):
            zoia.backend.metadata.initialize_metadata()

    def test_rename_key(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.backend.metadata._write_metadata({'foo': 'bar', 'baz': 'qux'})
        zoia.backend.metadata.rename_key('foo', 'quux')
        metadata = zoia.backend.metadata.load_metadata()
        self.assertEqual(metadata, {'quux': 'bar', 'baz': 'qux'})

    def test_rename_key_existing_key(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.backend.metadata._write_metadata({'foo': 'bar', 'baz': 'qux'})
        with self.assertRaises(KeyError):
            zoia.backend.metadata.rename_key('quuz', 'foo')

        with self.assertRaises(KeyError):
            zoia.backend.metadata.rename_key('foo', 'baz')


class TestMetadatum(unittest.TestCase):
    def test_metadatum_from_dict(self):
        d = {
            'title': 'foo',
            'authors': ['John Doe', 'Jane Roe'],
            'year': 2001,
        }
        metadatum = zoia.backend.metadata.Metadatum.from_dict(d)
        self.assertEqual(metadatum.title, 'foo')
        self.assertEqual(metadatum.authors, [['John', 'Doe'], ['Jane', 'Roe']])
        self.assertEqual(metadatum.year, 2001)

    def test_metadatum_str(self):
        metadatum = zoia.backend.metadata.Metadatum(
            authors=['John Doe', 'Jane Roe'],
            year=2001,
            title='Foo',
        )

        self.assertEqual(str(metadatum), 'Doe & Roe (2001), "Foo"')


class TestGetArxivIds(unittest.TestCase):
    @unittest.mock.patch('zoia.backend.metadata.load_metadata')
    def test_get_arxiv_ids(self, mock_load_metadata):
        mock_load_metadata.return_value = {
            'doe09-foo': {'arxiv_id': '0901.0123'},
            'roe19-baz': {'isbn': '9781499999990'},
            'smith10-bar': {'arxiv_id': '1002.1001'},
        }

        arxiv_ids = zoia.backend.metadata.get_arxiv_ids()
        self.assertEqual(arxiv_ids, {'0901.0123', '1002.1001'})


class TestGetIsbns(unittest.TestCase):
    @unittest.mock.patch('zoia.backend.metadata.load_metadata')
    def test_get_isbns(self, mock_load_metadata):
        mock_load_metadata.return_value = {
            'doe09-foo': {'arxiv_id': '0901.0123'},
            'roe19-baz': {'isbn': '9781499999990'},
            'smith10-bar': {'arxiv_id': '1002.1001'},
        }

        isbns = zoia.backend.metadata.get_isbns()
        self.assertEqual(isbns, {'9781499999990'})


class TestGetDois(unittest.TestCase):
    @unittest.mock.patch('zoia.backend.metadata.load_metadata')
    def test_get_dois(self, mock_load_metadata):
        mock_load_metadata.return_value = {
            'doe09-foo': {'arxiv_id': '0901.0123'},
            'roe19-baz': {'isbn': '9781499999990'},
            'smith10-bar': {'doi': '10.1000/foo'},
        }

        dois = zoia.backend.metadata.get_dois()
        self.assertEqual(dois, {'10.1000/foo'})


class TestGetMd5s(unittest.TestCase):
    @unittest.mock.patch('zoia.backend.metadata.load_metadata')
    def test_get_dois(self, mock_load_metadata):
        mock_load_metadata.return_value = {
            'doe09-foo': {'arxiv_id': '0901.0123'},
            'roe19-baz': {'isbn': '9781499999990'},
            'smith10-bar': {'doi': '10.1000/foo'},
            'johnson11-qux': {'md5': '2aa5d113c95b2432dbdb7c6440115774'},
        }

        md5_hashes = zoia.backend.metadata.get_md5_hashes()
        self.assertEqual(md5_hashes, {'2aa5d113c95b2432dbdb7c6440115774'})
