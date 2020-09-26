import tempfile
import unittest
import unittest.mock
from pathlib import Path

from click.testing import CliRunner

from ..context import zoia
import zoia.cli


class TestOpen(unittest.TestCase):
    @unittest.mock.patch('zoia.backend.config.load_config')
    @unittest.mock.patch('zoia.cli.open.click.launch')
    def test_open(self, mock_launch, mock_load_config):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            config = zoia.backend.config.ZoiaConfig(library_root=tmpdir)
            mock_load_config.return_value = config

            doc_dir = Path(tmpdir) / 'bar01-baz'
            doc_dir.mkdir()
            doc_path = doc_dir / 'document.pdf'
            doc_path.touch()

            result = runner.invoke(zoia.cli.zoia, ['open', 'bar01-baz'])
            self.assertEqual(result.exit_code, 0)
