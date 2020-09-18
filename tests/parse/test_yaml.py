import unittest
from textwrap import dedent

from ..context import zoia
import zoia.parse.yaml


class TestYaml(unittest.TestCase):
    def test_yaml_dump(self):
        d = {
            'foo': 'bar',
            'baz': [1, 2],
        }

        observed_str = zoia.parse.yaml.dump(d)
        expected_str = dedent(
            '''\
            foo: bar
            baz:
                - 1
                - 2
            '''
        )

        self.assertEqual(observed_str, expected_str)

    def test_remove_header(self):
        text = dedent(
            '''\
            ---
            foo: bar
            baz:
                - 1
                - 2
            ---
            Hello world.
            '''
        )

        body = zoia.parse.yaml.remove_header(text)

        self.assertEqual(body, 'Hello world.\n')
