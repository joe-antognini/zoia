import os
import tempfile
import unittest
import unittest.mock

from .context import zoia
import zoia.config


class TestConfig(unittest.TestCase):
    @unittest.mock.patch('zoia.config.os.getenv')
    def test_get_config_filepath(self, mock_getenv):
        mock_getenv.return_value = '/home/foo/.config'
        observed_filepath = zoia.config.get_config_filepath()
        expected_filepath = '/home/foo/.config/zoia/config.yaml'
        self.assertEqual(observed_filepath, expected_filepath)

    @unittest.mock.patch('zoia.config.get_config_filepath')
    def test_load_config_empty(self, mock_config_filepath):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_config_filepath.return_value = os.path.join(
                tmpdir, 'zoia/config.yaml'
            )
            config = zoia.config.load_config()
        self.assertEqual(config, {})

    @unittest.mock.patch('zoia.config.get_config_filepath')
    def test_save_load_config(self, mock_config_filepath):
        config = {'directory': '/foo/bar'}
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_config_filepath.return_value = os.path.join(
                tmpdir, 'zoia/config.yaml'
            )
            zoia.config.save_config(config)
            observed_config = zoia.config.load_config()
        self.assertEqual(observed_config, config)


class TestLibraryRoot(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.patcher = unittest.mock.patch('zoia.config.get_config_filepath')
        self.mock_config_filepath = self.patcher.start()
        self.mock_config_filepath.return_value = os.path.join(
            self.tmpdir.name, 'zoia/config.yaml'
        )

    def tearDown(self):
        self.tmpdir.cleanup()
        self.patcher.stop()

    def test_get_library_root_empty(self):
        library_root = zoia.config.get_library_root()
        self.assertIsNone(library_root)

    def test_set_get_library_root(self):
        zoia.config.set_library_root('foo')
        observed_library_root = zoia.config.get_library_root()
        self.assertEqual(observed_library_root, 'foo')
