import tempfile
import unittest
import unittest.mock
from pathlib import Path

from .context import zoia
import zoia.metadata


@unittest.mock.patch('zoia.metadata.get_library_root')
class TestMetadata(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir.name

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_write_load_metadata(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.metadata._write_metadata({'foo': 'bar'})
        metadata = zoia.metadata.load_metadata()
        self.assertEqual(metadata, {'foo': 'bar'})

    def test_append_metadata(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.metadata._write_metadata({'foo': 'bar'})
        zoia.metadata.append_metadata('baz', 'qux')
        metadata = zoia.metadata.load_metadata()
        self.assertEqual(metadata, {'foo': 'bar', 'baz': 'qux'})

    def test_initialize_metadata(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        self.assertFalse((Path(self.tmpdir) / '.metadata.json').exists())
        zoia.metadata.initialize_metadata()
        self.assertTrue((Path(self.tmpdir) / '.metadata.json').exists())

    def test_initialize_metadata_already_existing(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        (Path(self.tmpdir) / '.metadata.json').touch()
        with self.assertRaises(RuntimeError):
            zoia.metadata.initialize_metadata()

    def test_rename_key(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.metadata._write_metadata({'foo': 'bar', 'baz': 'qux'})
        zoia.metadata.rename_key('foo', 'quux')
        metadata = zoia.metadata.load_metadata()
        self.assertEqual(metadata, {'quux': 'bar', 'baz': 'qux'})

    def test_rename_key_existing_key(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.metadata._write_metadata({'foo': 'bar', 'baz': 'qux'})
        with self.assertRaises(KeyError):
            zoia.metadata.rename_key('quuz', 'foo')

        with self.assertRaises(KeyError):
            zoia.metadata.rename_key('foo', 'baz')
