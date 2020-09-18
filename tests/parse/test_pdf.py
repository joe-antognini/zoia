import os
import tempfile
import unittest
from pathlib import Path

from ..context import zoia
import zoia.parse.pdf


class TestPdf(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_is_pdf_no_file(self):
        self.assertFalse(
            zoia.parse.pdf.is_pdf(os.path.join(self.tmpdir.name, 'foo.pdf'))
        )

    def test_is_pdf_empty_file(self):
        (Path(self.tmpdir.name) / 'foo.pdf').touch()
        self.assertFalse(
            zoia.parse.pdf.is_pdf(os.path.join(self.tmpdir.name, 'foo.pdf'))
        )

    def test_is_pdf_good_pdf(self):
        with open(os.path.join(self.tmpdir.name, 'foo.pdf'), 'wb') as fp:
            fp.write(b'%PDF')

        self.assertTrue(
            zoia.parse.pdf.is_pdf(os.path.join(self.tmpdir.name, 'foo.pdf'))
        )


class TestGetDoiFromPdf(unittest.TestCase):
    @unittest.mock.patch('zoia.parse.pdf.extract_text')
    def test_get_doi_from_pdf_valid_doi(self, mock_extract_text):
        mock_extract_text.return_value = (
            'foo bar doi: 10.1093/mnras/stv1552\n baz qux'
        )

        self.assertEqual(
            zoia.parse.pdf.get_doi_from_pdf(None), '10.1093/mnras/stv1552'
        )

    @unittest.mock.patch('zoia.parse.pdf.extract_text')
    def test_get_doi_from_pdf_no_doi(self, mock_extract_text):
        mock_extract_text.return_value = 'foo bar doi: baz'

        self.assertIsNone(zoia.parse.pdf.get_doi_from_pdf(None))
