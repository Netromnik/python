# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand

from irk.news.models import Article, Podcast
from irk.news.controllers.socials.social_card import PodcastSocialCardCreator


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Преобразование подкастов в статьях в нормальные материалы типа Подкаст'

    def handle(self, **options):
        log.debug('Started migrate podcasts')

        redirects = []
        common_fields = [
            'stamp', 'published_time', 'subject', 'subject_main', 'category', 'title', 'slug', 'author', 'caption',
            'is_hidden', 'is_super', 'comments_cnt', 'source_site', 'home_position',
            'views_cnt', 'popularity', 'vk_share_cnt', 'tw_share_cnt', 'ok_share_cnt', 'fb_share_cnt',
            'hide_comments', 'disable_comments', 'social_text', 'social_label', 'introduction'
        ]

        for article in Article.objects.filter(project__slug='podcasting').order_by('stamp'):
            link, content = self._separate_link(article)
            podcast = Podcast.objects.create(
                link=link,
                content=content,
                **{field: getattr(article, field, None) for field in common_fields}
            )
            self.carry_m2m(article, podcast)
            self.create_social_card(podcast)
            podcast.save()
            redirects.append((article.get_absolute_url(), podcast.get_absolute_url()))

        self.stdout.write('Redirect table:')
        for redirect in redirects:
            self.stdout.write('rewrite ^{} {}'.format(*redirect))

        log.debug('Finished migrate podcasts')

    def carry_m2m(self, article, podcast):
        """"""

        for site in article.sites.all():
            podcast.sites.add(site)

        for tag in article.tags.all():
            podcast.tags.add(tag)

    def create_social_card(self, podcast):
        creator = PodcastSocialCardCreator(podcast)
        creator.create()

    def _separate_link(self, article):
        soup = BeautifulSoup(article.content)

        return soup.iframe.get('src'), soup.get_text()

