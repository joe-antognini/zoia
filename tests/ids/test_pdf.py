import os
import tempfile
import unittest
from pathlib import Path

from ..context import zoia
import zoia.ids.pdf


class TestPdf(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_is_pdf_no_file(self):
        self.assertFalse(
            zoia.ids.pdf.is_pdf(os.path.join(self.tmpdir.name, 'foo.pdf'))
        )

    def test_is_pdf_empty_file(self):
        (Path(self.tmpdir.name) / 'foo.pdf').touch()
        self.assertFalse(
            zoia.ids.pdf.is_pdf(os.path.join(self.tmpdir.name, 'foo.pdf'))
        )

    def test_is_pdf_good_pdf(self):
        with open(os.path.join(self.tmpdir.name, 'foo.pdf'), 'wb') as fp:
            fp.write(b'%PDF')

        self.assertTrue(
            zoia.ids.pdf.is_pdf(os.path.join(self.tmpdir.name, 'foo.pdf'))
        )
