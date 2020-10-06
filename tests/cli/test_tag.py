import unittest.mock

from click.testing import CliRunner

from ..context import zoia

import zoia.cli
from tests.fixtures.metadata import ZoiaUnitTest


class TestTag(ZoiaUnitTest):
    @unittest.mock.patch('zoia.cli.tag.zoia.backend.config.load_config')
    def test_tag(self, mock_load_config):
        mock_load_config.return_value = self.config
        metadatum = zoia.backend.metadata.Metadatum(
            entry_type='article',
            title='Foo',
            authors=['John Doe'],
            year=2001,
        )
        self.metadata.append('doe01-foo', metadatum.to_dict())

        runner = CliRunner()
        result = runner.invoke(
            zoia.cli.zoia, ['tag', 'doe01-foo', 'bar', 'baz']
        )

        self.assertEqual(result.exit_code, 0)

        metadata = zoia.backend.json.JSONMetadata(config=self.config)
        self.assertEqual(metadata['doe01-foo']['tags'], ['bar', 'baz'])
