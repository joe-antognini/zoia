import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from click.testing import CliRunner

from .context import zoia
import zoia.init


class TestIsValidInitDir(unittest.TestCase):
    def test__is_valid_init_dir_none(self):
        self.assertFalse(zoia.init._is_valid_init_dir(None))

    def test__is_valid_init_dir_no_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            directory = os.path.join(tmpdir, 'foo')
            self.assertTrue(zoia.init._is_valid_init_dir(directory))

    def test__is_valid_init_dir_exists_and_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(zoia.init._is_valid_init_dir(tmpdir))

    def test__is_valid_init_dir_exists_not_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'foo').touch()
            self.assertFalse(zoia.init._is_valid_init_dir(tmpdir))


@unittest.mock.patch('zoia.init._is_valid_init_dir')
@unittest.mock.patch('zoia.init.os.getcwd')
class TestGetDefaultDirectory(unittest.TestCase):
    def test__get_default_directory_cwd(
        self, mock_getcwd, mock_is_valid_init_dir
    ):
        mock_getcwd.return_value = '/home/foo'
        mock_is_valid_init_dir.side_effect = lambda x: x == '/home/foo'
        observed_default_directory = zoia.init._get_default_directory()
        expected_default_directory = '/home/foo'
        self.assertEqual(
            observed_default_directory, expected_default_directory
        )

    def test__get_default_directory_subdir(
        self, mock_getcwd, mock_is_valid_init_dir
    ):
        mock_getcwd.return_value = '/home/foo'
        mock_is_valid_init_dir.side_effect = lambda x: x == '/home/foo/zoia'
        observed_default_directory = zoia.init._get_default_directory()
        expected_default_directory = '/home/foo/zoia'
        self.assertEqual(
            observed_default_directory, expected_default_directory
        )

    def test__get_default_directory_none(
        self, mock_getcwd, mock_is_valid_init_dir
    ):
        mock_getcwd.return_value = '/home/foo'
        mock_is_valid_init_dir.side_effect = lambda x: False
        observed_default_directory = zoia.init._get_default_directory()
        self.assertIsNone(observed_default_directory)


class TestInit(unittest.TestCase):
    @unittest.mock.patch('zoia.init.zoia.metadata.write_metadata')
    @unittest.mock.patch('zoia.init.set_library_root')
    @unittest.mock.patch('zoia.init.get_library_root')
    def test_init_denovo(
        self, mock_library_root, mock_set_library_root, mock_write_metadata
    ):
        mock_library_root.return_value = None
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(zoia.init.init, input='\n')
            self.assertEqual(result.exit_code, 0)
            mock_set_library_root.assert_called_with(os.getcwd())
        mock_write_metadata.assert_called_once()
