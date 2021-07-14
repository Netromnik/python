# -*- coding: utf-8 -*-

"""Замена ContentType новостей и статей на ContentType материалов в голосованиях"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from irk.news.models import BaseMaterial, News, Article
from irk.polls.models import Poll


class Command(BaseCommand):
    def handle(self, *args, **options):
        news_ct = ContentType.objects.get_for_model(News)
        article_ct = ContentType.objects.get_for_model(Article)
        material_ct = ContentType.objects.get_for_model(BaseMaterial)
        for poll in Poll.objects.filter(target_ct_id__in=[news_ct, article_ct]):
            poll.target_ct_id = material_ct.pk
            poll.save()
