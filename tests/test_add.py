import json
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
            'authors': [['Michael', 'Kilgour'], ['Dvira', 'Segal']],
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
            entry['authors'],
            [['Christopher J.', 'Shallue'], ['Andrew', 'Vanderburg']],
        )


class TestGetIsbnMetadata(unittest.TestCase):
    @unittest.mock.patch('zoia.add.isbnlib.meta')
    def test__get_isbn_metadata(self, mock_meta):
        mock_meta.return_value = {
            'ISBN-13': '9781400848898',
            'Title': 'Modern Classical Physics',
            'Authors': ['Kip S. Thorne', 'Roger D. Blandford'],
            'Publisher': 'Princeton University Press',
            'Year': '2017',
            'Language': 'en',
        }

        observed_metadata = zoia.add._get_isbn_metadata('9781400848898')

        expected_metadata = {
            'isbn': '9781400848898',
            'title': 'Modern Classical Physics',
            'authors': [['Kip S.', 'Thorne'], ['Roger D.', 'Blandford']],
            'publisher': 'Princeton University Press',
            'year': 2017,
            'language': 'en',
        }

        self.assertEqual(observed_metadata, expected_metadata)


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
            'authors': [['Michael', 'Kilgour'], ['Dvira', 'Segal']],
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
            'authors': [['Michael', 'Kilgour'], ['Dvira', 'Segal']],
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


class TestAddIsbn(unittest.TestCase):
    @unittest.mock.patch('zoia.add.zoia.config.get_library_root')
    @unittest.mock.patch('zoia.add.zoia.metadata.append_metadata')
    @unittest.mock.patch('zoia.add.zoia.citekey.create_citekey')
    @unittest.mock.patch('zoia.add._get_isbn_metadata')
    @unittest.mock.patch('zoia.add.zoia.metadata.get_isbns')
    def test__add_isbn(
        self,
        mock_get_isbns,
        mock_get_isbn_metadata,
        mock_create_citekey,
        mock_append_metadata,
        mock_get_library_root,
    ):
        mock_get_isbns.return_value = {}

        metadata = {
            'authors': [['Kip', 'Thorne'], ['Roger', 'Blandford']],
            'title': 'Modern Classical Physics',
            'year': '2017',
        }
        mock_get_isbn_metadata.return_value = metadata
        mock_citekey = 'thorne+blandford17-modern'
        mock_create_citekey.return_value = mock_citekey

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_library_root.return_value = tmpdir
            zoia.add._add_isbn(identifier='9781400848898', citekey=None)

            self.assertTrue((Path(tmpdir) / mock_citekey).is_dir())

        mock_append_metadata.assert_called_once_with(mock_citekey, metadata)


class TestAddDoi(unittest.TestCase):
    @unittest.mock.patch('zoia.add.zoia.metadata.get_dois')
    @unittest.mock.patch('zoia.add.requests.get')
    @unittest.mock.patch('zoia.add._get_doi_metadata')
    @unittest.mock.patch('zoia.add.zoia.citekey.create_citekey')
    @unittest.mock.patch('zoia.add.zoia.config.get_library_root')
    @unittest.mock.patch('zoia.add.zoia.metadata.append_metadata')
    def test__add_doi(
        self,
        mock_append_metadata,
        mock_get_library_root,
        mock_create_citekey,
        mock__get_doi_metadata,
        mock_requests_get,
        mock_get_dois,
    ):
        mock_get_dois.return_value = {}

        mock_arxiv_response = unittest.mock.MagicMock()
        mock_arxiv_response.status_code = 200
        mock_arxiv_response.text = json.dumps({'arxivId': '1504.05957'})

        mock_pdf_response = unittest.mock.MagicMock()
        mock_pdf_response.status_code = 200
        mock_pdf_response.content = b'%PDF'

        def requests_side_effect(url):
            semantic_scholar_url = (
                'https://api.semanticscholar.org/v1/paper/10.1093/mnras/'
                'stv1552'
            )
            if url == semantic_scholar_url:
                return mock_arxiv_response
            elif url == 'https://arxiv.org/pdf/1504.05957.pdf':
                return mock_pdf_response
            else:
                raise ValueError(f'Bad url {url}')

        mock_requests_get.side_effect = requests_side_effect

        mock__get_doi_metadata.return_value = {
            'authors': [['J.', 'Antognini']],
            'title': 'Timescales of Kozai-Lidov oscillations',
            'year': 2015,
        }

        citekey = 'antognini15-timescales'
        mock_create_citekey.return_value = citekey

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_get_library_root.return_value = tmpdir
            citekey = zoia.add._add_doi('10.1093/mnras/stv1552', citekey=None)

            self.assertTrue(
                (Path(tmpdir) / citekey / 'document.pdf').is_file()
            )

        mock_append_metadata.assert_called_once_with(
            'antognini15-timescales',
            {
                'authors': [['J.', 'Antognini']],
                'title': 'Timescales of Kozai-Lidov oscillations',
                'year': 2015,
                'arxiv_id': '1504.05957',
            },
        )
