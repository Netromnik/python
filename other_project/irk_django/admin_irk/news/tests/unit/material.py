# -*- coding: utf-8 -*-

import datetime

from django_dynamic_fixture import G

from django.contrib.contenttypes.models import ContentType

from irk.magazine.models import Magazine
from irk.news.models import Article as NewsArticle
from irk.news.models import BaseMaterial, Category
from irk.obed.models import Article as ObedArticle
from irk.options.models import Site
from irk.special.models import Project
from irk.tests.unit_base import UnitTestBase


def create_material(app_label, model_name, **kwargs):

    ct = ContentType.objects.get_by_natural_key(app_label, model_name)

    # Хак для приложения Эксперта, пока не будет соответствия между app_label и Site.slugs
    if app_label == 'experts':
        app_label = 'expert'

    site = kwargs.pop('site', None) or Site.objects.get(slugs=app_label)
    sites = kwargs.pop('sites', None) or [site]

    return G(ct.model_class(), content_type=ct, source_site=site, sites=sites, **kwargs)


class MaterialAbsoluteUrlTest(UnitTestBase):
    """Тесты формирования url для материалов"""

    def test_news_materials(self):
        """Материалы новостей"""

        news = self.create_material('news', 'news', slug='test_news', stamp=datetime.date(2016, 1, 1))
        self.assertEqual('/news/20160101/test_news/', str(news.get_absolute_url()))
        base_news = BaseMaterial.objects.get(pk=news.pk)
        self.assertEqual('/news/20160101/test_news/', str(base_news.get_absolute_url()))

        news_with_bb_code = self.create_material(
            'news', 'news', slug='test_news', stamp=datetime.date(2016, 1, 1),
            title='test [url http://example.com]link[/url] test'
        )
        self.assertEqual('http://example.com', str(news_with_bb_code.get_absolute_url()))
        base_news_with_bb_code = BaseMaterial.objects.get(pk=news_with_bb_code.pk)
        self.assertEqual('http://example.com', str(base_news_with_bb_code.get_absolute_url()))

        article = self.create_material('news', 'article', slug='test_article', stamp=datetime.date(2016, 1, 2))
        self.assertEqual('/news/articles/20160102/test_article/', str(article.get_absolute_url()))
        base_article = BaseMaterial.objects.get(pk=article.pk)
        self.assertEqual('/news/articles/20160102/test_article/', str(base_article.get_absolute_url()))

        photo = self.create_material('news', 'photo', slug='test_photo', stamp=datetime.date(2016, 1, 3))
        self.assertEqual('/news/photo/20160103/test_photo/', str(photo.get_absolute_url()))
        base_photo = BaseMaterial.objects.get(pk=photo.pk)
        self.assertEqual('/news/photo/20160103/test_photo/', str(base_photo.get_absolute_url()))

        video = self.create_material('news', 'video', slug='test_video', stamp=datetime.date(2016, 1, 4))
        self.assertEqual('/news/video/20160104/test_video/', str(video.get_absolute_url()))
        base_video = BaseMaterial.objects.get(pk=video.pk)
        self.assertEqual('/news/video/20160104/test_video/', str(base_video.get_absolute_url()))

        info = self.create_material('news', 'infographic')
        self.assertEqual('/news/graphics/{}/'.format(info.pk), str(info.get_absolute_url()))
        base_info = BaseMaterial.objects.get(pk=info.pk)
        self.assertEqual('/news/graphics/{}/'.format(info.pk), str(base_info.get_absolute_url()))

        metamaterial = self.create_material('news', 'metamaterial', url='http://example.com')
        self.assertEqual('http://example.com', str(metamaterial.get_absolute_url()))
        base_metamaterial = BaseMaterial.objects.get(pk=metamaterial.pk)
        self.assertEqual('http://example.com', str(base_metamaterial.get_absolute_url()))

        poll = self.create_material('news', 'poll')
        self.assertEqual('/news/poll/{}/'.format(poll.pk), str(poll.get_absolute_url()))
        base_poll = BaseMaterial.objects.get(pk=poll.pk)
        self.assertEqual('/news/poll/{}/'.format(poll.pk), str(base_poll.get_absolute_url()))

    def test_expert(self):
        """Эксперт"""

        category = G(Category, slug='test_category')
        site = Site.objects.get(slugs='expert')
        material = self.create_material('experts', 'expert', category=category, site=site)
        self.assertEqual('/news/expert/test_category/{}/'.format(material.pk), str(material.get_absolute_url()))

        base_material = BaseMaterial.objects.get(pk=material.pk)
        self.assertEqual('/news/expert/test_category/{}/'.format(material.pk), str(base_material.get_absolute_url()))

    def test_afisha_materials(self):
        """Материалы афиши"""

        site = Site.objects.get(slugs='afisha')

        article = self.create_material(
            'afisha', 'article', site=site, slug='test_article', stamp=datetime.date(2016, 1, 1)
        )
        self.assertEqual('/afisha/articles/20160101/test_article/', str(article.get_absolute_url()))
        base_article = BaseMaterial.objects.get(pk=article.pk)
        self.assertEqual('/afisha/articles/20160101/test_article/', str(base_article.get_absolute_url()))

        review = self.create_material(
            'afisha', 'review', site=site, slug='test_review', stamp=datetime.date(2016, 1, 1)
        )
        self.assertEqual('/afisha/reviews/20160101/test_review/', str(review.get_absolute_url()))
        base_review = BaseMaterial.objects.get(pk=review.pk)
        self.assertEqual('/afisha/reviews/20160101/test_review/', str(base_review.get_absolute_url()))

        photo = self.create_material(
            'afisha', 'photo', site=site, slug='test_photo', stamp=datetime.date(2016, 1, 1)
        )
        self.assertEqual('/afisha/photo/20160101/test_photo/', str(photo.get_absolute_url()))
        base_photo = BaseMaterial.objects.get(pk=photo.pk)
        self.assertEqual('/afisha/photo/20160101/test_photo/', str(base_photo.get_absolute_url()))

        poll = self.create_material('afisha', 'poll')
        self.assertEqual('/afisha/poll/{}/'.format(poll.pk), str(poll.get_absolute_url()))

    def test_obed_materials(self):
        """Материалы обеда"""

        article = self.create_material('obed', 'article', slug='test_article', stamp=datetime.date(2016, 1, 1))
        self.assertEqual('/obed/articles/20160101/test_article/', str(article.get_absolute_url()))
        base_article = BaseMaterial.objects.get(pk=article.pk)
        self.assertEqual('/obed/articles/20160101/test_article/', str(base_article.get_absolute_url()))

        review = self.create_material('obed', 'review')
        url = '/obed/columnist/article/{}/'.format(review.pk)
        self.assertEqual(url, str(review.get_absolute_url()))
        base_review = BaseMaterial.objects.get(pk=review.pk)
        self.assertEqual(url, str(base_review.get_absolute_url()))
        obed_article = ObedArticle.objects.get(pk=review.pk)
        self.assertEqual(url, str(obed_article.get_absolute_url()))
        news_article = NewsArticle.objects.get(pk=review.pk)
        self.assertEqual(url, str(news_article.get_absolute_url()))

        poll = self.create_material('obed', 'poll')
        self.assertEqual('/obed/poll/{}/'.format(poll.pk), str(poll.get_absolute_url()))

    def test_tourism_materials(self):
        """Материалы туризма"""

        news = self.create_material(
            'tourism', 'news', slug='test_news', stamp=datetime.date(2016, 1, 1)
        )
        self.assertEqual('/tourism/news/20160101/test_news/', str(news.get_absolute_url()))

        article = self.create_material(
            'tourism', 'article', slug='test_article', stamp=datetime.date(2016, 1, 1)
        )
        self.assertEqual('/tourism/blog/20160101/test_article/', str(article.get_absolute_url()))
        base_article = BaseMaterial.objects.get(pk=article.pk)
        self.assertEqual('/tourism/blog/20160101/test_article/', str(base_article.get_absolute_url()))
        news_article = ContentType.objects.get_by_natural_key('news', 'article').get_object_for_this_type(pk=article.pk)
        self.assertEqual('/tourism/blog/20160101/test_article/', str(news_article.get_absolute_url()))

        info = self.create_material('tourism', 'infographic')
        self.assertEqual('/tourism/graphics/{}/'.format(info.pk), str(info.get_absolute_url()))

        poll = self.create_material('tourism', 'poll')
        self.assertEqual('/tourism/poll/{}/'.format(poll.pk), str(poll.get_absolute_url()))

    def test_currency_materials(self):
        """Материалы валюты"""

        news = self.create_material('currency', 'news', slug='test_news', stamp=datetime.date(2016, 1, 1))
        self.assertEqual('/currency/news/20160101/test_news/', str(news.get_absolute_url()))

    def test_magazine_materials(self):
        """Материалы из журнала"""

        magazine_first = G(Magazine, slug='first')
        project_family = G(Project, slug='family')

        article = self.create_material('news', 'article', magazine=magazine_first, project=project_family)
        self.assertEqual('/magazine/first/{}/'.format(article.pk), str(article.get_absolute_url()))

        photo = self.create_material(
            'afisha', 'photo', slug='test_photo', magazine=magazine_first, stamp=datetime.date(2016, 1, 1)
        )
        self.assertEqual('/magazine/first/{}/'.format(photo.pk), str(photo.get_absolute_url()))

        photo.magazine = None
        photo.save()
        self.assertEqual('/afisha/photo/20160101/test_photo/', str(photo.get_absolute_url()))

        test = self.create_material('obed', 'test', magazine=magazine_first)
        self.assertEqual('/magazine/first/{}/'.format(test.pk), str(test.get_absolute_url()))

    def test_project_materials(self):
        """Материалы из спец проектов"""

        project_club = G(Project, slug='club')
        article = self.create_material('tourism', 'article', project=project_club)
        self.assertEqual('/tourism/club/article/{}/'.format(article.pk), str(article.get_absolute_url()))

        project_jazz = G(Project, slug='jazz')
        photo = self.create_material('afisha', 'photo', project=project_jazz)
        self.assertEqual('/afisha/jazz/photo/{}/'.format(photo.pk), str(photo.get_absolute_url()))

        project_family = G(Project, slug='family')
        info = self.create_material('news', 'infographic', project=project_family)
        self.assertEqual('/news/family/graphics/{}/'.format(info.pk), str(info.get_absolute_url()))

    def create_material(self, *args, **kwargs):
        """Перегружаем основную функцию, так как заполненеие nullable полей ломает тесты"""

        kwargs.setdefault('fill_nullable_fields', False)

        return create_material(*args, **kwargs)


class MaterialAdminUrlTest(UnitTestBase):
    """Тесты формирования админки url для материалов"""

    models = [
        ('news', 'news'),
        ('news', 'article'),
        ('news', 'photo'),
        ('news', 'video'),
        ('news', 'infographic'),
        ('news', 'metamaterial'),
        ('news', 'poll'),
        ('afisha', 'article'),
        ('afisha', 'review'),
        ('afisha', 'photo'),
        ('afisha', 'poll'),
        ('obed', 'article'),
        ('obed', 'review'),
        ('obed', 'poll'),
        ('tourism', 'news'),
        ('tourism', 'article'),
        ('tourism', 'infographic'),
        ('tourism', 'poll'),
        ('currency', 'news'),
        ('experts', 'expert'),
    ]

    def test_main(self):
        """Проверка формирования url в админке"""

        for app_label, model_name in self.models:
            material = create_material(app_label, model_name)
            self.assertEqual('/adm/{}/{}/{}/change/'.format(app_label, model_name, material.pk),
                             material.get_admin_url())
