import os
import unittest
import unittest.mock
from pathlib import Path
from textwrap import dedent

from click.testing import CliRunner

from ..context import zoia
from ..fixtures.metadata import ZoiaUnitTest
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


class TestNote(ZoiaUnitTest):
    @unittest.mock.patch('zoia.cli.note.zoia.backend.config.load_config')
    @unittest.mock.patch('zoia.cli.note.click.edit')
    def test_note_no_existing_note(self, mock_edit, mock_load_config):
        runner = CliRunner()

        mock_load_config.return_value = self.config
        doc_dir = Path(self.config.library_root) / 'doe01-foo'
        doc_dir.mkdir()
        self.metadata._metadata = {
            'doe01-foo': {
                'entry_type': 'article',
                'title': 'Foo',
                'authors': [['John', 'Doe']],
                'year': 2001,
            },
        }
        self.metadata.write()

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
