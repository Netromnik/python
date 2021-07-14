from __future__ import absolute_import

from django.contrib.auth.models import User
from django_dynamic_fixture import get

from irk.blogs.models import Author
from irk.blogs.permissions import is_blog_author

from irk.tests.unit_base import UnitTestBase


class BlogAuthorTestCase(UnitTestBase):
    def test_index(self):
        author = get(Author, is_visible=True)
        self.assertTrue(is_blog_author(author))

        blocked_author = get(Author, is_visible=False)
        self.assertFalse(is_blog_author(blocked_author))

        user = get(User)
        self.assertFalse(is_blog_author(user))
