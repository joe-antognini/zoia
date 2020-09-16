import unittest
from textwrap import dedent

from .context import zoia
import zoia.yaml


class TestYamlDump(unittest.TestCase):
    def test_yaml_dump(self):
        d = {
            'foo': 'bar',
            'baz': [1, 2],
        }

        observed_str = zoia.yaml.dump(d)
        expected_str = dedent(
            '''\
            foo: bar
            baz:
                - 1
                - 2
            '''
        )

        self.assertEqual(observed_str, expected_str)
