import os
import tempfile
import unittest

from ..context import zoia  # noqa: F401
from zoia.parse.classification import IdType
from zoia.parse.classification import classify_identifier
from zoia.parse.classification import classify_and_normalize_identifier


class TestClassifyIdentifier(unittest.TestCase):
    def test_classify_identifier_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'foo.pdf')
            with open(filename, 'wb') as fp:
                fp.write(b'%PDF')

            observed_id_type = classify_identifier(filename)
            expected_id_type = IdType.PDF
            self.assertEqual(observed_id_type, expected_id_type)

    def test_classify_identifier_arxiv(self):
        identifier = '2001.00001'
        observed_id_type = classify_identifier(identifier)
        expected_id_type = IdType.ARXIV
        self.assertEqual(observed_id_type, expected_id_type)

    def test_classify_identifier_isbn(self):
        identifier = '9780691159027'
        observed_id_type = classify_identifier(identifier)
        expected_id_type = IdType.ISBN
        self.assertEqual(observed_id_type, expected_id_type)

    def test_classify_identifier_doi(self):
        identifier = '10.1000/foo'
        observed_id_type = classify_identifier(identifier)
        expected_id_type = IdType.DOI
        self.assertEqual(observed_id_type, expected_id_type)


class TestClassifyAndNormalizeIdentifier(unittest.TestCase):
    def test_classify_and_normalize_identifier_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'foo.pdf')
            with open(filename, 'wb') as fp:
                fp.write(b'%PDF')

            (
                observed_id_type,
                normalized_identifier,
            ) = classify_and_normalize_identifier(filename)
            expected_id_type = IdType.PDF
            self.assertEqual(observed_id_type, expected_id_type)
            self.assertEqual(normalized_identifier, filename)

    def test_classify_and_normalize_identifier_arxiv(self):
        identifier = 'arxiv:2001.00001v2'
        (
            observed_id_type,
            normalized_identifier,
        ) = classify_and_normalize_identifier(identifier)
        expected_id_type = IdType.ARXIV
        self.assertEqual(observed_id_type, expected_id_type)
        self.assertEqual(normalized_identifier, '2001.00001')

    def test_classify_and_normalize_identifier_isbn(self):
        identifier = '978-0-691159-02-7'
        (
            observed_id_type,
            normalized_identifier,
        ) = classify_and_normalize_identifier(identifier)
        expected_id_type = IdType.ISBN
        self.assertEqual(observed_id_type, expected_id_type)
        self.assertEqual(normalized_identifier, '9780691159027')

    def test_classify_and_normalize_identifier_doi(self):
        identifier = 'doi:10.1000/foo'
        (
            observed_id_type,
            normalized_identifier,
        ) = classify_and_normalize_identifier(identifier)
        expected_id_type = IdType.DOI
        self.assertEqual(observed_id_type, expected_id_type)
        self.assertEqual(normalized_identifier, '10.1000/foo')
