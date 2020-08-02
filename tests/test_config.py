import tempfile
import unittest

from .context import zoia
import zoia.config


class TestLibraryRoot(unittest.TestCase):
    def test_get_library_root_empty(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            self.assertIsNone(zoia.config.get_library_root(tmpfile.name))

    def test_set_get_library_root(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            zoia.config.set_library_root('foo', tmpfile.name)
            observed_library_root = zoia.config.get_library_root(tmpfile.name)
            self.assertEqual(observed_library_root, 'foo')
