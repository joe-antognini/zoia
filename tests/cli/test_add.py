import json
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import requests

from ..context import zoia
from ..fixtures.metadata import ZoiaUnitTest
import zoia.backend.json
import zoia.cli.add


class TestValidateResponse(unittest.TestCase):
    def test__validate_response(self):
        response = requests.Response()
        response.status_code = 200
        self.assertTrue(zoia.cli.add._validate_response(response, None))

    def test__validate_response_invalid(self):
        response = requests.Response()
        response.status_code = 404
        with self.assertRaises(zoia.cli.add.ZoiaExternalApiException):
            self.assertFalse(zoia.cli.add._validate_response(response, None))

        response.status_code = 300
        with self.assertRaises(zoia.cli.add.ZoiaExternalApiException):
            self.assertFalse(zoia.cli.add._validate_response(response, None))


class TestGetArxivMetadata(unittest.TestCase):
    @unittest.mock.patch('zoia.cli.add.requests.get')
    def test__get_arxiv_metadata(self, mock_requests_get):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        with open(
            os.path.join(
                os.path.dirname(__file__), '../fixtures/arxiv_response.xml'
            )
        ) as fp:
            response.text = fp.read()

        mock_requests_get.return_value = response

        observed_metadata = zoia.cli.add._get_arxiv_metadata('1601.00001')
        expected_metadata = {
            'entry_type': 'article',
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
    @unittest.mock.patch('zoia.cli.add.requests.get')
    def test__get_doi_metadata(self, mock_requests_get):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        with open(
            os.path.join(
                os.path.dirname(__file__), '../fixtures/doi_response.bib'
            )
        ) as fp:
            response.text = fp.read()

        mock_requests_get.return_value = response

        entry = zoia.cli.add._get_doi_metadata('10.3847/1538-3881/aa9e09')
        self.assertEqual(entry['year'], 2018)
        self.assertEqual(
            entry['authors'],
            [['Christopher J.', 'Shallue'], ['Andrew', 'Vanderburg']],
        )


class TestGetIsbnMetadata(unittest.TestCase):
    @unittest.mock.patch('zoia.cli.add.isbnlib.meta')
    def test__get_isbn_metadata(self, mock_meta):
        mock_meta.return_value = {
            'ISBN-13': '9781400848898',
            'Title': 'Modern Classical Physics',
            'Authors': ['Kip S. Thorne', 'Roger D. Blandford'],
            'Publisher': 'Princeton University Press',
            'Year': '2017',
            'Language': 'en',
        }

        observed_metadata = zoia.cli.add._get_isbn_metadata('9781400848898')

        expected_metadata = {
            'entry_type': 'book',
            'isbn': '9781400848898',
            'title': 'Modern Classical Physics',
            'authors': [['Kip S.', 'Thorne'], ['Roger D.', 'Blandford']],
            'publisher': 'Princeton University Press',
            'year': 2017,
            'language': 'en',
        }

        self.assertEqual(observed_metadata, expected_metadata)


class TestAddArxivId(unittest.TestCase):
    @unittest.mock.patch('zoia.cli.add._get_doi_metadata')
    @unittest.mock.patch('zoia.cli.add._get_arxiv_metadata')
    @unittest.mock.patch('zoia.cli.add.requests.get')
    def test__add_arxiv_id(
        self,
        mock_requests_get,
        mock_get_arxiv_metadata,
        mock_get_doi_metadata,
    ):
        response = unittest.mock.MagicMock()
        response.status_code = 200
        response.content = b'\xde\xad\xbe\xef'
        mock_requests_get.return_value = response

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
            'entry_type': 'article',
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
            library_root = Path(tmpdir) / 'library'
            library_root.mkdir()
            db_root = Path(tmpdir) / 'metadata'
            db_root.mkdir()
            config = zoia.backend.config.ZoiaConfig(
                library_root=library_root, db_root=db_root
            )
            metadata = zoia.backend.json.JSONMetadata(config)
            zoia.cli.add._add_arxiv_id(metadata, '1601.00001')

            document_path = (
                library_root / 'kilgour+segal16-inelastic/document.pdf'
            )
            self.assertTrue(document_path.exists())


class TestAddIsbn(ZoiaUnitTest):
    @unittest.mock.patch('zoia.cli.add.zoia.parse.citekey.create_citekey')
    @unittest.mock.patch('zoia.cli.add._get_isbn_metadata')
    def test__add_isbn(
        self,
        mock_get_isbn_metadata,
        mock_create_citekey,
    ):
        metadatum = {
            'authors': [['Kip', 'Thorne'], ['Roger', 'Blandford']],
            'title': 'Modern Classical Physics',
            'year': '2017',
        }
        mock_get_isbn_metadata.return_value = metadatum
        mock_citekey = 'thorne+blandford17-modern'
        mock_create_citekey.return_value = mock_citekey

        zoia.cli.add._add_isbn(
            self.metadata, identifier='9781400848898', citekey=None
        )

        self.assertTrue(
            (Path(self.config.library_root) / mock_citekey).is_dir()
        )


class TestAddDoi(ZoiaUnitTest):
    @unittest.mock.patch('zoia.cli.add.requests.get')
    @unittest.mock.patch('zoia.cli.add._get_doi_metadata')
    @unittest.mock.patch('zoia.cli.add.zoia.parse.citekey.create_citekey')
    def test__add_doi(
        self,
        mock_create_citekey,
        mock__get_doi_metadata,
        mock_requests_get,
    ):
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

        zoia.cli.add._add_doi(
            self.metadata, '10.1093/mnras/stv1552', citekey=None
        )

        self.assertTrue(
            (
                Path(self.config.library_root) / citekey / 'document.pdf'
            ).is_file()
        )


class TestAddPdf(ZoiaUnitTest):
    @unittest.mock.patch('zoia.cli.add.click.confirm')
    @unittest.mock.patch('zoia.cli.add._get_doi_metadata')
    @unittest.mock.patch('zoia.cli.add.zoia.parse.pdf.get_doi_from_pdf')
    def test__add_pdf(
        self,
        mock_get_doi_from_pdf,
        mock_get_doi_metadata,
        mock_click_confirm,
    ):
        identifier = os.path.join(self.config.library_root, 'foo.pdf')
        with open(identifier, 'wb') as fp:
            fp.write(b'%PDF')

        mock_get_doi_from_pdf.return_value = '10.1000/foo'
        mock_metadata = {
            'title': 'Foo',
            'authors': [['John', 'Doe']],
            'year': 1999,
        }
        mock_get_doi_metadata.return_value = mock_metadata

        mock_click_confirm.return_value = True

        zoia.cli.add._add_pdf(
            self.metadata, identifier, citekey=None, move_paper=False
        )

        self.assertTrue(
            (
                Path(self.config.library_root) / 'doe99-foo/document.pdf'
            ).is_file()
        )
