import os
import tempfile
import unittest
import unittest.mock

from click.testing import CliRunner

from .context import zoia
import zoia.init


class TestInit(unittest.TestCase):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile()
        self.config_filename = self.config_file.name

    def tearDown(self):
        self.config_file.close()

    def test_init_denovo(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with unittest.mock.patch(
                'zoia.init.ZOIA_CONFIG_ROOT', self.config_filename
            ):
                result = runner.invoke(zoia.init.init, input='\n')
                self.assertEqual(result.exit_code, 0)
                self.assertTrue(os.path.isfile('.metadata.json'))
