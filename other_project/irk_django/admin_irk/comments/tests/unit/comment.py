# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.comments.models import Comment
from irk.tests.unit_base import UnitTestBase
from irk.news.tests.unit.material import create_material


class CommentViewTest(UnitTestBase):

    def setUp(self):
        self.material = create_material('news', 'news')
        self.url = self.material.get_comments_url()

    def test_default(self):
        c1 = G(Comment, text='comment 1', target=self.material)
        c2 = G(Comment, text='comment 2', target=self.material, parent=c1)
        c3 = G(Comment, text='comment 3', target=self.material, parent=c1)
        c4 = G(Comment, text='comment 4', target=self.material, parent=c2)
        c5 = G(Comment, text='comment 5', target=self.material, parent=c4)
        c6 = G(Comment, text='comment 6', target=self.material, parent=c1)

        response = self.app.get(self.url, xhr=True)
        self.assertStatusIsOk(response)

    def test_show_hidden(self):
        raise NotImplementedError

    def test_top_10(self):
        raise NotImplementedError

    def test_sorted(self):
        raise NotImplementedError
