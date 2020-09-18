import unittest

from ..context import zoia
import zoia.parse.arxiv


class TestArxivValidIds(unittest.TestCase):
    def test__is_valid_old_style_arxiv_id(self):
        self.assertFalse(zoia.parse.arxiv._is_valid_old_style_arxiv_id('foo'))
        self.assertFalse(zoia.parse.arxiv._is_valid_old_style_arxiv_id('123'))
        self.assertTrue(
            zoia.parse.arxiv._is_valid_old_style_arxiv_id('astro-ph/9901001')
        )
        self.assertFalse(
            zoia.parse.arxiv._is_valid_old_style_arxiv_id('astro-ph/9913001')
        )
        self.assertFalse(
            zoia.parse.arxiv._is_valid_old_style_arxiv_id('2001.00001')
        )

    def test__is_valid_new_style_arxiv_id(self):
        self.assertFalse(zoia.parse.arxiv._is_valid_new_style_arxiv_id('foo'))
        self.assertFalse(zoia.parse.arxiv._is_valid_new_style_arxiv_id('123'))
        self.assertTrue(
            zoia.parse.arxiv._is_valid_new_style_arxiv_id('2001.00001')
        )
        self.assertFalse(
            zoia.parse.arxiv._is_valid_new_style_arxiv_id('20.0100001')
        )
        self.assertFalse(
            zoia.parse.arxiv._is_valid_new_style_arxiv_id('astro-ph/9901001')
        )
        self.assertTrue(
            zoia.parse.arxiv._is_valid_new_style_arxiv_id('2001.00001v2')
        )
        self.assertFalse(
            zoia.parse.arxiv._is_valid_new_style_arxiv_id('2001.00001v2v')
        )
        self.assertFalse(
            zoia.parse.arxiv._is_valid_new_style_arxiv_id('2001.00001v2foo')
        )

    def test_is_arxiv(self):
        self.assertFalse(zoia.parse.arxiv.is_arxiv('foo'))
        self.assertFalse(zoia.parse.arxiv.is_arxiv('123'))
        self.assertTrue(zoia.parse.arxiv.is_arxiv('arXiv:2001.00001'))
        self.assertTrue(zoia.parse.arxiv.is_arxiv('arXiv:astro-ph/9901001'))


class TestNormalize(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(
            zoia.parse.arxiv.normalize('2001.00001'), '2001.00001'
        )

        self.assertEqual(
            zoia.parse.arxiv.normalize('arXiv:2001.00001'), '2001.00001'
        )

        self.assertEqual(
            zoia.parse.arxiv.normalize('http://www.arxiv.org/abs/2001.00001'),
            '2001.00001',
        )

        self.assertEqual(
            zoia.parse.arxiv.normalize('https://www.arxiv.org/abs/2001.00001'),
            '2001.00001',
        )

        self.assertEqual(
            zoia.parse.arxiv.normalize('https://arxiv.org/abs/2001.00001'),
            '2001.00001',
        )

        self.assertEqual(
            zoia.parse.arxiv.normalize('https://arxiv.org/pdf/2001.00001'),
            '2001.00001',
        )

        self.assertEqual(
            zoia.parse.arxiv.normalize('https://arxiv.org/pdf/2001.00001.pdf'),
            '2001.00001',
        )

        self.assertEqual(
            zoia.parse.arxiv.normalize('arxiv.org/pdf/2001.00001.pdf'),
            '2001.00001',
        )
