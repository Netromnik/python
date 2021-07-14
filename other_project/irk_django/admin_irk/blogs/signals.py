# -*- coding: utf-8 -*-

from django.db.models import Sum


def author_recount(sender, instance, **kwargs):
    """Пересчет счетчиков о количестве постов/подписчиков у автора блогов"""

    from irk.blogs.models import Author, UserBlogEntry

    entries_cnt = UserBlogEntry.objects.filter(author_id=instance.author_id, visible=True).count() or 0
    comments_cnt = UserBlogEntry.objects.filter(author_id=instance.author_id).aggregate(
        Sum('comments_cnt'))['comments_cnt__sum'] or 0

    Author.objects.filter(pk=instance.author_id).update(entries_cnt=entries_cnt, comments_cnt=comments_cnt)
