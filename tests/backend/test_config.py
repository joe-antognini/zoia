import os
import tempfile
import unittest
import unittest.mock

from ..context import zoia
import zoia.backend.config


class TestZoiaConfigDataclass(unittest.TestCase):
    def test_zoia_config_to_dict(self):
        config = zoia.backend.config.ZoiaConfig(
            library_root='/tmp/foo',
            db_root='/tmp/bar',
            backend=zoia.backend.config.ZoiaBackend.JSON,
        )

        expected_dict = {
            'library_root': '/tmp/foo',
            'db_root': '/tmp/bar',
            'backend': 'json',
        }
        self.assertEqual(config.to_dict(), expected_dict)


class TestConfig(unittest.TestCase):
    @unittest.mock.patch('zoia.backend.config.os.getenv')
    def test_get_config_filepath(self, mock_getenv):
        mock_getenv.return_value = '/home/foo/.config'
        observed_filepath = zoia.backend.config.get_config_filepath()
        expected_filepath = '/home/foo/.config/zoia/config.yaml'
        self.assertEqual(observed_filepath, expected_filepath)

    @unittest.mock.patch('zoia.backend.config.get_config_filepath')
    def test_load_config_empty(self, mock_config_filepath):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_config_filepath.return_value = os.path.join(
                tmpdir, 'zoia/config.yaml'
            )
            config = zoia.backend.config.load_config()
        self.assertIsNone(config)

    @unittest.mock.patch('zoia.backend.config._get_db_root')
    def test_save_load_config(self, mock_get_db_root):
        config = zoia.backend.config.ZoiaConfig(
            library_root='/foo/bar', db_root='/baz/qux'
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_db_root.return_value = '/baz/qux'
            config_filepath = os.path.join(tmpdir, 'zoia/config.yaml')
            zoia.backend.config.save_config(config, config_filepath)
            observed_config = zoia.backend.config.load_config(config_filepath)
        self.assertEqual(observed_config, config)


class TestLibraryRoot(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.patcher = unittest.mock.patch(
            'zoia.backend.config.get_config_filepath'
        )
        self.mock_config_filepath = self.patcher.start()
        self.mock_config_filepath.return_value = os.path.join(
            self.tmpdir.name, 'zoia/config.yaml'
        )

    def tearDown(self):
        self.tmpdir.cleanup()
        self.patcher.stop()


class TestDatabaseDir(unittest.TestCase):
    @unittest.mock.patch('zoia.backend.config.os.getenv')
    def test_get_database_dir_no_envvar(self, mock_getenv):
        def _mock_getenv(envvar, default=None):
            if envvar == 'HOME':
                return '/home/foo'
            else:
                return default

        mock_getenv.side_effect = _mock_getenv

        observed_db_dir = zoia.backend.config._get_db_root()
        expected_db_dir = '/home/foo/.local/share/zoia'

        self.assertEqual(observed_db_dir, expected_db_dir)

    @unittest.mock.patch('zoia.backend.config.os.getenv')
    def test_get_database_dir_with_envvar(self, mock_getenv):
        def _mock_getenv(envvar, default=None):
            if envvar == 'HOME':
                return '/home/foo'
            elif envvar == 'XDG_DATA_HOME':
                return '/home/foo/zoia_data'
            else:
                return default

        mock_getenv.side_effect = _mock_getenv

        observed_db_dir = zoia.backend.config._get_db_root()
        expected_db_dir = '/home/foo/zoia_data'

        self.assertEqual(observed_db_dir, expected_db_dir)
