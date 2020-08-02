import tempfile
import unittest
import unittest.mock

from .context import zoia
import zoia.metadata


class TestMetadata(unittest.TestCase):

    @unittest.mock.patch('zoia.metadata.get_library_root')
    def test_write_load_metadata(self, mock_get_library_root):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_library_root.return_value = tmpdir
            zoia.metadata.write_metadata({'foo': 'bar'})
            metadata = zoia.metadata.load_metadata()
            self.assertEqual(metadata, {'foo': 'bar'})
