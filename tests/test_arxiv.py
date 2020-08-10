import unittest

from .context import zoia
import zoia.arxiv


class TestArxivValidIds(unittest.TestCase):
    def test__is_valid_old_style_arxiv_id(self):
        self.assertFalse(zoia.arxiv._is_valid_old_style_arxiv_id('foo'))
        self.assertFalse(zoia.arxiv._is_valid_old_style_arxiv_id('123'))
        self.assertTrue(
            zoia.arxiv._is_valid_old_style_arxiv_id('astro-ph/9901001')
        )
        self.assertFalse(
            zoia.arxiv._is_valid_old_style_arxiv_id('astro-ph/9913001')
        )
        self.assertFalse(zoia.arxiv._is_valid_old_style_arxiv_id('2001.00001'))

    def test__is_valid_new_style_arxiv_id(self):
        self.assertFalse(zoia.arxiv._is_valid_new_style_arxiv_id('foo'))
        self.assertFalse(zoia.arxiv._is_valid_new_style_arxiv_id('123'))
        self.assertTrue(zoia.arxiv._is_valid_new_style_arxiv_id('2001.00001'))
        self.assertFalse(zoia.arxiv._is_valid_new_style_arxiv_id('20.0100001'))
        self.assertFalse(
            zoia.arxiv._is_valid_new_style_arxiv_id('astro-ph/9901001')
        )

    def test_is_valid_arxiv_id(self):
        self.assertFalse(zoia.arxiv.is_valid_arxiv_id('foo'))
        self.assertFalse(zoia.arxiv.is_valid_arxiv_id('123'))
        self.assertTrue(zoia.arxiv.is_valid_arxiv_id('arXiv:2001.00001'))
        self.assertTrue(zoia.arxiv.is_valid_arxiv_id('arXiv:astro-ph/9901001'))
