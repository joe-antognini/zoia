import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import requests

from .context import zoia
import zoia.add


class TestValidateResponse(unittest.TestCase):
    def test__validate_response(self):
        response = requests.Response()
        response.status_code = 200
        self.assertTrue(zoia.add._validate_response(response, None))

    def test__validate_response_invalid(self):
        response = requests.Response()
        response.status_code = 404
        with self.assertRaises(zoia.add.ZoiaExternalApiException):
            self.assertFalse(zoia.add._validate_response(response, None))

        response.status_code = 300
        with self.assertRaises(zoia.add.ZoiaExternalApiException):
            self.assertFalse(zoia.add._validate_response(response, None))


class TestGetArxivMetadata(unittest.TestCase):
    @unittest.mock.patch('zoia.add.requests.get')
    def test__get_arxiv_metadata(self, mock_requests_get):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        with open(
            os.path.join(
                os.path.dirname(__file__), 'fixtures/arxiv_response.xml'
            )
        ) as fp:
            response.text = fp.read()

        mock_requests_get.return_value = response

        observed_metadata = zoia.add._get_arxiv_metadata('1601.00001')
        expected_metadata = {
            'arxiv_id': '1601.00001',
            'authors': ['Michael Kilgour', 'Dvira Segal'],
            'title': (
                'Inelastic effects in molecular transport junctions: The '
                'probe technique at high bias'
            ),
            'year': 2015,
            'month': 12,
            'doi': '10.1063/1.4944470',
        }

        self.assertEqual(observed_metadata, expected_metadata)


class TestGetDoiMetadata(unittest.TestCase):
    @unittest.mock.patch('zoia.add.requests.get')
    def test__get_doi_metadata(self, mock_requests_get):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        with open(
            os.path.join(
                os.path.dirname(__file__), 'fixtures/doi_response.bib'
            )
        ) as fp:
            response.text = fp.read()

        mock_requests_get.return_value = response

        entry = zoia.add._get_doi_metadata('10.3847/1538-3881/aa9e09')
        self.assertEqual(entry['year'], 2018)
        self.assertEqual(
            entry['author'], ['Shallue, Christopher J.', 'Vanderburg, Andrew']
        )


class TestAddArxivId(unittest.TestCase):
    @unittest.mock.patch('zoia.add.zoia.config.get_library_root')
    @unittest.mock.patch('zoia.add.zoia.metadata.get_arxiv_ids')
    @unittest.mock.patch('zoia.add.zoia.metadata.append_metadata')
    @unittest.mock.patch('zoia.add._get_doi_metadata')
    @unittest.mock.patch('zoia.add._get_arxiv_metadata')
    @unittest.mock.patch('zoia.add.requests.get')
    def test__add_arxiv_id(
        self,
        mock_requests_get,
        mock_get_arxiv_metadata,
        mock_get_doi_metadata,
        mock_append_metadata,
        mock_get_arxiv_ids,
        mock_get_library_root,
    ):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        response.content = b'\xde\xad\xbe\xef'
        mock_requests_get.return_value = response

        mock_get_arxiv_ids.return_value = {'doe99-foo', 'smith01-bar'}

        mock_get_arxiv_metadata.return_value = {
            'arxiv_id': '1601.00001',
            'authors': ['Michael Kilgour', 'Dvira Segal'],
            'title': (
                'Inelastic effects in molecular transport junctions: The '
                'probe technique at high bias'
            ),
            'year': 2015,
            'month': 12,
            'doi': '10.1063/1.4944470',
        }

        mock_get_doi_metadata.return_value = {
            'journal': 'The Journal of Chemical Physics',
            'title': (
                'Inelastic effects in molecular transport junctions: The '
                'probe technique at high bias'
            ),
            'author': ['Kilgour, Michael', 'Segal, Dvira'],
            'pages': '124107',
            'number': '12',
            'volume': '144',
            'publisher': '{AIP} Publishing',
            'month': 'mar',
            'year': 2016,
            'url': 'https://doi.org/10.1063%2F1.4944470',
            'doi': '10.1063/1.4944470',
            'ENTRYTYPE': 'article',
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_library_root.return_value = tmpdir

            zoia.add._add_arxiv_id('1601.00001')

            self.assertTrue(
                (
                    Path(tmpdir) / 'kilgour+segal16-inelastic/document.pdf'
                ).exists()
            )
