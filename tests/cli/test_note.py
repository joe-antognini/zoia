import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from textwrap import dedent

from click.testing import CliRunner

from ..context import zoia
import zoia.cli.note


class TestCreateHeader(unittest.TestCase):
    def test__create_header(self):
        metadatum = {
            'title': 'Foo',
            'authors': [['Jane', 'Roe'], ['John', 'Doe']],
            'year': 2001,
            'tags': ['bar', 'baz'],
        }

        observed_header = zoia.cli.note._create_header(metadatum)
        expected_header = dedent(
            '''\
            ---
            title: Foo
            authors:
                - Jane Roe
                - John Doe
            year: 2001
            tags: bar, baz
            ---
            '''
        )

        self.assertEqual(observed_header, expected_header)


class TestNote(unittest.TestCase):
    @unittest.mock.patch('zoia.cli.note.zoia.backend.config.get_library_root')
    @unittest.mock.patch('zoia.cli.note.zoia.backend.metadata.get_metadata')
    @unittest.mock.patch('zoia.cli.note.click.edit')
    def test_note_no_existing_note(
        self, mock_edit, mock_load_metadata, mock_get_library_root
    ):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_dir = Path(tmpdir) / 'doe01-foo'
            doc_dir.mkdir()
            mock_load_metadata.return_value = {
                'entry_type': 'article',
                'title': 'Foo',
                'authors': [['John', 'Doe']],
                'year': 2001,
            }
            mock_get_library_root.return_value = tmpdir

            mock_edit.return_value = dedent(
                '''\
                ---
                title: Foo
                authors:
                    - John Doe
                year: 2001
                ---
                Hello world.
                '''
            )
            result = runner.invoke(zoia.cli.zoia, args=['note', 'doe01-foo'])
            self.assertEqual(result.exit_code, 0)

            self.assertTrue(os.path.isfile(doc_dir / 'notes.md'))

            with open(doc_dir / 'notes.md') as fp:
                note_body = fp.read()

            self.assertEqual(note_body, 'Hello world.\n')
