import unittest

from ..context import zoia
import zoia.ids.isbn


class TestIsbn(unittest.TestCase):
    def test__isbn_has_valid_checksum_13_digit_isbn(self):
        self.assertTrue(
            zoia.ids.isbn._isbn_has_valid_checksum('9780691159027')
        )
        self.assertFalse(
            zoia.ids.isbn._isbn_has_valid_checksum('9780691159028')
        )

    def test__isbn_has_valid_checksum_10_digit_isbn(self):
        self.assertTrue(zoia.ids.isbn._isbn_has_valid_checksum('0716703440'))
        self.assertFalse(zoia.ids.isbn._isbn_has_valid_checksum('0716703441'))

    def test_is_isbn(self):
        self.assertFalse(zoia.ids.isbn.is_isbn('foo'))
        self.assertFalse(zoia.ids.isbn.is_isbn('012345'))
        self.assertFalse(zoia.ids.isbn.is_isbn('012345678910'))

        self.assertTrue(zoia.ids.isbn.is_isbn('0716703440'))
        self.assertTrue(zoia.ids.isbn.is_isbn('9780691159027'))

        self.assertFalse(zoia.ids.isbn.is_isbn('0716703441'))
        self.assertFalse(zoia.ids.isbn.is_isbn('9780691159028'))

        self.assertTrue(zoia.ids.isbn.is_isbn('0-7167-0344-0'))
        self.assertTrue(zoia.ids.isbn.is_isbn('978-0-69115-902-7'))
