import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from .context import zoia
import zoia.open


class TestOpen(unittest.TestCase):
    @unittest.mock.patch('zoia.open.zoia.config.get_library_root')
    @unittest.mock.patch('zoia.open.platform.system')
    @unittest.mock.patch('zoia.open.subprocess.call')
    def test_open(self, mock_call, mock_system, mock_get_library_root):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_library_root.return_value = tmpdir
            doc_dir = Path(tmpdir) / 'bar01-baz'
            doc_dir.mkdir()
            doc_path = doc_dir / 'document.pdf'
            doc_path.touch()

            mock_system.return_value = 'Linux'

            zoia.open._open('bar01-baz')
            mock_call.assert_called_once_with(
                ('xdg-open', os.path.join(tmpdir, 'bar01-baz/document.pdf'))
            )
