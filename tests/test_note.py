import tempfile
import unittest
import unittest.mock
from pathlib import Path

from click.testing import CliRunner

from .context import zoia
import zoia.cli


class TestNote(unittest.TestCase):
    @unittest.mock.patch('zoia.note.zoia.config.get_library_root')
    @unittest.mock.patch('zoia.note.zoia.metadata.load_metadata')
    @unittest.mock.patch('zoia.note.click.edit')
    def test_note_no_existing_note(
        self, mock_edit, mock_load_metadata, mock_get_library_root
    ):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / 'doe01-foo'
            doc_dir.mkdir()
            mock_load_metadata.return_value = {'doe01-foo': {}}
            mock_get_library_root.return_value = tmpdir

            result = runner.invoke(zoia.cli.zoia, ['note', 'doe01-foo'])
            self.assertEqual(result.exit_code, 0)
