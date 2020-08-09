import tempfile
import unittest
import unittest.mock

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
        zoia.metadata.write_metadata({'foo': 'bar'})
        metadata = zoia.metadata.load_metadata()
        self.assertEqual(metadata, {'foo': 'bar'})

    def test_append_metadata(self, mock_get_library_root):
        mock_get_library_root.return_value = self.tmpdir
        zoia.metadata.write_metadata({'foo': 'bar'})
        zoia.metadata.append_metadata('baz', 'qux')
        metadata = zoia.metadata.load_metadata()
        self.assertEqual(metadata, {'foo': 'bar', 'baz': 'qux'})
