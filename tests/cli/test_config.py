import os
import tempfile
import unittest
import unittest.mock

from click.testing import CliRunner

from ..context import zoia
import zoia.cli
import zoia.cli.config


class TestConfigValidator(unittest.TestCase):
    def test__config_validator_good_obj(self):
        good_obj = {
            'library_root': '/tmp/foo',
            'db_root': '/tmp/bar',
            'backend': 'json',
        }

        self.assertIsNone(zoia.cli.config._config_validator(good_obj))

    def test__config_validator_bad_obj(self):
        bad_obj = {
            'db_root': '/tmp/bar',
            'backend': 'json',
        }

        with self.assertRaises(zoia.parse.yaml.ZoiaYamlValidationError):
            zoia.cli.config._config_validator(bad_obj)

        bad_obj = {
            'library_root': '/tmp/foo',
            'db_root': '/tmp/bar',
            'backend': 'foo',
        }

        with self.assertRaises(zoia.parse.yaml.ZoiaYamlValidationError):
            zoia.cli.config._config_validator(bad_obj)


class TestConfig(unittest.TestCase):
    @unittest.mock.patch(
        'zoia.cli.config.zoia.backend.config.get_config_filepath'
    )
    @unittest.mock.patch('zoia.cli.config.zoia.parse.yaml.edit_until_valid')
    def test_config(self, mock_edit, mock_get_config_filepath):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_filename = os.path.join(tmpdir, 'config.yaml')
            mock_get_config_filepath.return_value = config_filename

            config = zoia.backend.config.ZoiaConfig(
                library_root='/tmp/foo', db_root='/tmp/bar', backend='sqlite'
            )
            zoia.backend.config.save_config(config, config_filename)

            config_dict = config.to_dict()
            config_dict['backend'] = 'json'
            mock_edit.return_value = config_dict

            runner = CliRunner()
            result = runner.invoke(zoia.cli.zoia, ['config'])

            self.assertEqual(result.exit_code, 0)

            new_config = zoia.backend.config.load_config(config_filename)
            self.assertEqual(
                new_config.backend, zoia.backend.config.ZoiaBackend.JSON
            )
