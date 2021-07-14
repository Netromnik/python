# -*- coding: utf-8 -*-

import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.news.models import ArticleType
from irk.news.tests.unit.material import create_material
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.afisha.models import Event, EventType, Genre, Guide, EventGuide, Period, Sessions


class ReviewTestCase(UnitTestBase):
    """ Тестирование рецензий """

    def setUp(self):
        super(ReviewTestCase, self).setUp()
        self.site = Site.objects.get(slugs='afisha')
        self.date = datetime.date.today()
        self.event_type = G(EventType, alias='cinema')

    def create_review(self, slug):
        genre = G(Genre)
        guide = G(Guide, event_type=self.event_type)
        event = G(Event, type=self.event_type, genre=genre, parent=None, is_hidden=False)
        event_guide = G(EventGuide, event=event, guide=guide, hall=None)
        period = G(Period, event_guide=event_guide, start_date=self.date, end_date=self.date)
        G(Sessions, period=period, time=datetime.time(23, 0))
        article_type = G(ArticleType)
        review = create_material(
            'afisha', 'review', event=event, type=article_type, stamp=self.date, sites=[self.site], slug=slug,
            article_ptr__type=article_type, site=self.site, is_hidden=False
        )
        return review

    def test_index(self):
        """Индекс рецензий"""

        review = self.create_review(slug=self.random_string(10).lower())
        page = self.app.get(reverse('afisha:review:index'))

        self.assertEqual(1, len(page.context['objects']))
        self.assertEqual(review, page.context['objects'][0])

    def test_read(self):
        """Рецензия по алиасу"""

        slug = self.random_string(10).lower()
        review = self.create_review(slug=slug)
        kwargs_ = {
            "year": self.date.year,
            "month": '%02d' % self.date.month,
            "day": '%02d' % self.date.day,
            "slug": slug
        }
        page = self.app.get(reverse('afisha:review:read', kwargs=kwargs_))

        self.assertEqual(page.status_code, 200)
        self.assertEqual(review, page.context['object'])
