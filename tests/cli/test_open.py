import tempfile
import unittest
import unittest.mock
from pathlib import Path

from click.testing import CliRunner

from ..context import zoia
import zoia.cli


class TestOpen(unittest.TestCase):
    @unittest.mock.patch('zoia.cli.open.zoia.backend.config.get_library_root')
    @unittest.mock.patch('zoia.cli.open.click.launch')
    def test_open(self, mock_launch, mock_get_library_root):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_library_root.return_value = tmpdir
            doc_dir = Path(tmpdir) / 'bar01-baz'
            doc_dir.mkdir()
            doc_path = doc_dir / 'document.pdf'
            doc_path.touch()

            result = runner.invoke(zoia.cli.zoia, ['open', 'bar01-baz'])
            self.assertEqual(result.exit_code, 0)
