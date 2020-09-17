import unittest
import unittest.mock

from .context import zoia
import zoia.pdf


class TestGetDoiFromPdf(unittest.TestCase):
    @unittest.mock.patch('zoia.pdf.extract_text')
    def test_get_doi_from_pdf_valid_doi(self, mock_extract_text):
        mock_extract_text.return_value = (
            'foo bar doi: 10.1093/mnras/stv1552\n baz qux'
        )

        self.assertEqual(
            zoia.pdf.get_doi_from_pdf(None), '10.1093/mnras/stv1552'
        )

    @unittest.mock.patch('zoia.pdf.extract_text')
    def test_get_doi_from_pdf_no_doi(self, mock_extract_text):
        mock_extract_text.return_value = 'foo bar doi: baz'

        self.assertIsNone(zoia.pdf.get_doi_from_pdf(None))
