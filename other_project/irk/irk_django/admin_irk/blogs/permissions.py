# -*- coding: utf-8 -*-

from irk.blogs.models import Author, BlogEntry


def is_blog_author(user):
    if not user.is_authenticated:
        return False

    return Author.objects.filter(pk=user.pk, is_visible=True, is_operative=True).exists()


def can_edit_blog(user, obj):
    if not user.is_authenticated:
        return False

    if isinstance(obj, Author):
        if user.pk == obj.pk:
            return True

    if isinstance(obj, BlogEntry):
        if user.pk == obj.author.pk:
            return True

    return False
