# -*- coding: utf-8 -*-

from __future__ import absolute_import

from irk.tests.unit_base import UnitTestBase
from irk.blogs.helpers import parse_caption


class ParseCaptionTestCase(UnitTestBase):
    def test(self):
        content = '''12345

        67890'''

        caption = '''12345'''

        self.assertEqual(caption, parse_caption(content))

    def test_bb_codes(self):
        content = '''[image 12345]

        67890'''

        caption = '''67890'''

        self.assertEqual(caption, parse_caption(content))
