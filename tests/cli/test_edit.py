import unittest
import unittest.mock

import json
from copy import copy

from click.testing import CliRunner

from ..context import zoia
from ..fixtures.metadata import ZoiaUnitTest
import zoia.cli


class TestEdit(ZoiaUnitTest):
    @unittest.mock.patch('zoia.cli.note.zoia.backend.config.load_config')
    @unittest.mock.patch('zoia.cli.note.click.edit')
    def test_edit(self, mock_edit, mock_load_config):
        mock_load_config.return_value = self.config

        self.metadata._metadata = {
            'doe+roe01-foo': {
                'authors': [['John', 'Doe'], ['Jane', 'Roe']],
                'title': 'Foo',
                'year': 2001,
            },
        }
        self.metadata.write()

        new_metadata = copy(self.metadata._metadata['doe+roe01-foo'])
        new_metadata['year'] = 2002

        mock_edit.return_value = json.dumps(new_metadata)

        runner = CliRunner()
        result = runner.invoke(
            zoia.cli.zoia, ['edit', 'doe+roe01-foo', '--syntax', 'json']
        )
        self.assertEqual(result.exit_code, 0)

        metadata = zoia.backend.metadata.get_metadata(self.config)
        self.assertEqual(metadata['doe+roe01-foo']['year'], 2002)
