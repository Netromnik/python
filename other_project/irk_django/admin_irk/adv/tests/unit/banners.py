# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
import datetime
from unittest import skip

from django.template import Template, Context, TemplateSyntaxError
from irk.adv.models import Place, Banner, Period, Targetix
from irk.currency.models import CurrencyCbrf
from django.contrib.staticfiles.finders import find
from django.core.urlresolvers import reverse


from django.core.files import File
from django.conf import settings
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase
from irk.options.models import Site
from irk.phones.models import MetaSection


class BannerPlacesTestCase(UnitTestBase):
    """Smoke-тест вывода баннеров на главных страницах разделов"""

    # Грузим фикстуру с местами на ирк.ру, так как их id захардкожены по шаблонам
    fixtures = UnitTestBase.fixtures + [os.path.join(settings.BASE_PATH, 'irk/adv/fixtures/adv_places.json'), ]

    def load_banners(self, site):
        places = Place.objects.filter(site=site)
        today = datetime.date.today()
        for place in places:
            banner = G(Banner, iframe='', places=[place, ])
            G(Period, banner=banner, date_from=today, date_to=today)

    def setUp(self):
        super(BannerPlacesTestCase, self).setUp()
        G(CurrencyCbrf, visible=True, stamp=datetime.date.today() + datetime.timedelta(days=-1))
        G(CurrencyCbrf, visible=True, stamp=datetime.date.today())

        # для блока форума в туризме
        G(MetaSection, id=1, alias='rent')
        G(MetaSection, id=2)

    def test_main_pages(self):
        sites = Site.objects.filter(is_hidden=False).exclude(slugs__in=['realty', 'currency', 'sms'])
        for site in sites:
            self.load_banners(site)
            response = self.app.get(site.url)
            self.assertEqual(response.status_code, 200, "Error open site %s" % site.slugs)


class BannersTestCase(UnitTestBase):

    def setUp(self):
        super(BannersTestCase, self).setUp()
        place = self.place = G(Place)
        banner = G(Banner, iframe='', places=[place, ])
        today = datetime.date.today()
        G(Period, banner=banner, date_from=today, date_to=today)

    def test_default(self):
        """Тестирование баннера, выводящегося по умолчанию в виджете"""

        site = Site.objects.get(slugs='home')
        site.widget_image = File(open(find('img/irkru.png')), 'irkru.png')
        site.widget_text = self.random_string(10)
        site.save()

        response = self.app.get(reverse('home_index'))

        self.assertIn(site.widget_text, response.content)

    def test_default2(self):
        """Выводит обычный код для баннерного места"""
        context = Context({})

        with self.assertTemplateUsed('adv/div_none.html'):
            result = Template('{{% load adv_tags %}}{{% ibanner ID={} %}}'.format(self.place.id)).render(context)

        self.assertIn('/ibr/block/{}'.format(self.place.id), result)

    def test_params_values_from_context(self):
        """Айдишник баннера берется из контекста"""
        place_id = self.place.id
        context = Context({'place_id': place_id})

        result = Template('{% load adv_tags %}{% ibanner ID=place_id %}').render(context)

        self.assertIn('/ibr/block/{}'.format(place_id), result)

    def test_as_variable(self):
        """ibanner сохраняет результат в переменной контекста"""
        tpl = '{% load adv_tags %}{% ibanner ID=444 as banner %}'

        banner = G(Banner, iframe='', places=[G(Place, id=444), ])
        today = datetime.date.today()
        G(Period, banner=banner, date_from=today, date_to=today)

        context = Context()
        result = Template(tpl).render(context)

        self.assertEqual(result.strip(), '')
        self.assertIn('/ibr/block/444', context.get('banner', ''))


class AdaptiveBannersTest(UnitTestBase):
    def test_targetix(self):
        """Таргетикс работает"""

        code = '<strong>Hello World</strong>'
        G(Place, id=1, targetix=G(Targetix, code=code), targetix2=None)

        result = Template('{% load adv_tags %}{% adaptive_banner mobile_id=1 %}').render(Context())
        self.assertIn(code, result)

    def test_default(self):
        """Баннер вообще в принципе выводится"""

        today = datetime.date.today()

        # мобильный
        banner = G(Banner, iframe='', places=[G(Place, id=1)])
        G(Period, banner=banner, date_from=today, date_to=today)

        # десктопный
        banner = G(Banner, iframe='', places=[G(Place, id=2)])
        G(Period, banner=banner, date_from=today, date_to=today)

        with self.assertTemplateUsed('adv/adaptive_banner.html'):
            result = Template('{% load adv_tags %}{% adaptive_banner mobile_id=1 desktop_id=2 %}').render(Context())

        self.assertIn('/ibr/block/1-', result)
        self.assertIn('/ibr/block/2-', result)

    def test_adaptive_banner_content(self):
        """Шаблон adaptive_banner_content (часто используемый) работает нормально"""

        today = datetime.date.today()

        # мобильный
        banner = G(Banner, iframe='', places=[G(Place, id=100)])
        G(Period, banner=banner, date_from=today, date_to=today)

        with self.assertTemplateUsed('adv/adaptive_banner_content.html'):
            result = Template("{% load adv_tags %}{% adaptive_banner mobile_id=100 template='adv/adaptive_banner_content.html' %}").render(Context())

        self.assertIn('/ibr/block/100-', result)

    @skip('пока нет такого функционала')
    def test_id_value_from_context(self):
        """Айдишник баннера можно передать в переменной контекста"""

        today = datetime.date.today()
        place = G(Place, id=1)
        banner = G(Banner, iframe='', places=[place])
        G(Period, banner=banner, date_from=today, date_to=today)

        context = Context({'place_id': 1})
        result = Template('{% load adv_tags %}{% adaptive_banner mobile_id=place_id %}').render(context)
        self.assertIn('/ibr/block/{}'.format(place.id), result)


class TargetixBannersTest(UnitTestBase):

    def test_single_external_banner(self):
        """Если нет нашего баннера, но есть внешний"""

        t = G(Targetix, code='<hello world/>')
        place = G(Place, targetix=t, targetix2=None)
        tpl = '{% load adv_tags %}{% ibanner ID='+str(place.id)+' %}'  # прости Господи

        context = Context({})
        result = Template(tpl).render(context)

        self.assertIn('<hello world/>', result)

    def test_no_banners_no_targetix(self):
        place = G(Place, id=474, targetix=None, targetix2=None)
        tpl = '{% load adv_tags %}{% ibanner ID=474 %}'

        result = Template(tpl).render(Context())
        self.assertEqual(result.strip(), '')

    def test_as_variable(self):
        """Таргетикс возвращается в переменной контекста AS var"""

        code = '<strong>Hello World</strong>'
        tpl = '{% load adv_tags %}{% ibanner ID=100 as banner %}'

        context = Context()
        place = G(Place, id=100, targetix=G(Targetix, code=code), targetix2=None)

        result = Template(tpl).render(context)
        self.assertEqual(result, '')
        self.assertIn(code, context.get('banner', ''))

    def test_two_external_banners(self):
        """
        targetix1__code и targetix2__code выводятся оба
        """
        t1 = G(Targetix, code='<alice>')
        t2 = G(Targetix, code='<bob>')
        place = G(Place, id=5, targetix=t1, targetix2=t2)

        tpl = '{% load adv_tags %}{% ibanner ID=5 %}'

        alice = bob = 0
        for i in range(11):
            result = Template(tpl).render(Context())
            self.assertTrue(('alice' in result) or ('bob' in result))
            if 'alice' in result:
                alice += 1
            if 'bob' in result:
                bob += 1

        # после десяти итераций у нас и боб и алиса хоть раз были
        self.assertTrue(alice > 0)
        self.assertTrue(bob > 0)

    @skip('это пока не реализовано, у нас рандомный вывод, не последовательный')
    def test_two_external_banners_serial(self):
        """
        Если стоит targetix1 и targetix2 - они выводятся по очереди
        """
        t1 = G(Targetix, code='<alice>')
        t2 = G(Targetix, code='<bob>')
        place = G(Place, targetix=t1, targetix2=t2)

        tpl = '{% load adv_tags %}{% ibanner ID='+str(place.id)+' %}'
        context = Context({})

        alice = bob = 0
        for i in range(7):
            result = Template(tpl).render(context)
            self.assertTrue(('alice' in result) or ('bob' in result))
            if 'alice' in result:
                alice += 1
            if 'bob' in result:
                bob += 1

        # после шести итераций у нас три боба и три алисы
        self.assertEqual(alice, 3)
        self.assertEqual(bob, 3)


class HasBannerTest(UnitTestBase):
    """Тесты шаблонного тега has_banner"""

    def test_normal(self):
        # поставим баннер на место 1
        today = datetime.date.today()
        place = G(Place, id=1)
        banner = G(Banner, iframe='', places=[place])
        G(Period, banner=banner, date_from=today, date_to=today)

        context = Context()
        template = '{% load adv_tags %}{% has_banner id=1 as has_banner_1%}'
        result = Template(template).render(context)

        self.assertIn('has_banner_1', context)
        self.assertTrue(context['has_banner_1'])
        self.assertEquals(result, '')

    def test_no_banner(self):
        """Если место есть, а баннера нет, вернет False"""
        place = G(Place, id=1)
        context = Context()
        template = '{% load adv_tags %}{% has_banner id=1 as has_banner_1%}'
        result = Template(template).render(context)

        self.assertIn('has_banner_1', context)
        self.assertFalse(context['has_banner_1'])
        self.assertEquals(result, '')

    def test_no_place(self):
        """Если нет даже места"""
        context = Context()
        template = '{% load adv_tags %}{% has_banner id=1 as has_banner_1%}'
        result = Template(template).render(context)

        self.assertIn('has_banner_1', context)
        self.assertEquals(context['has_banner_1'], False)
        self.assertEquals(result, '')
