import unittest
import unittest.mock

import json
from copy import copy

from click.testing import CliRunner

from ..context import zoia
import zoia.cli


class TestEdit(unittest.TestCase):
    @unittest.mock.patch(
        'zoia.cli.note.zoia.backend.metadata.replace_metadata'
    )
    @unittest.mock.patch('zoia.cli.note.zoia.backend.metadata.get_metadata')
    @unittest.mock.patch('zoia.cli.note.click.edit')
    def test_edit(self, mock_edit, mock_load_metadata, mock_replace_metadata):

        orig_metadata = {
            'authors': [['John', 'Doe'], ['Jane', 'Roe']],
            'title': 'Foo',
            'year': 2001,
        }
        new_metadata = copy(orig_metadata)
        new_metadata['year'] = 2002

        mock_load_metadata.return_value = orig_metadata
        mock_edit.return_value = json.dumps(new_metadata)

        runner = CliRunner()
        result = runner.invoke(
            zoia.cli.zoia, ['edit', 'doe+roe01-foo', '--syntax', 'json']
        )
        self.assertEqual(result.exit_code, 0)

        mock_replace_metadata.assert_called_once_with(
            'doe+roe01-foo', new_metadata
        )
