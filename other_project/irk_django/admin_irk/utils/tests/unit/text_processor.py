# -*- coding: utf-8 -*-

from __future__ import absolute_import

import textwrap

import bleach
from django_dynamic_fixture import G
from lxml.html import fromstring as html_fromstring

from django.contrib.staticfiles.finders import find
from django.core.files import File as DjangoFile

from irk.gallery.models import GalleryPicture, Picture
from irk.tests.unit_base import UnitTestBase
from irk.utils.models import TweetEmbed
from irk.utils.text.processors.default import processor
from irk.utils.text.processors.zen import processor as zen_processor


def create_picture():
    image = DjangoFile(open(find('img/irkru.png')))
    picture = G(Picture, image=image)

    return G(GalleryPicture, picture=picture)


class TextProcessorTest(UnitTestBase):
    def test_bb_codes(self):
        self.assertProcesses('[b]test[/b]', '<strong>test</strong>')
        self.assertProcesses('This [b]is[/b] test', 'This <strong>is</strong> test')
        self.assertProcesses('[i]test[/i]', '<em>test</em>')
        self.assertProcesses('[u]test[/u]', '<u>test</u>')
        self.assertProcesses('[s]test[/s]', '<del>test</del>')
        self.assertProcesses('[q]test[/q]', '<blockquote>test</blockquote>')
        self.assertProcesses('[h2]test[/h2]', '<h2>test</h2>')
        self.assertProcesses('[h3]test[/h3]', '<h3>test</h3>')
        self.assertProcesses('[cite]test[/cite]', '<div class="the-thought"><div>test</div></div>')
        self.assertProcesses('[intro]test[/intro]', '')
        self.assertProcesses('abc [intro]test[/intro] qwer', 'abc  qwer')

        self.assertProcesses('[email vp@example.org]Vasiliy Pupkin[/email]', '<a href="mailto:vp@example.org">Vasiliy Pupkin</a>')
        self.assertProcesses('[email foo+bar@example.org]Foo bar[/email]', '<a href="mailto:foo+bar@example.org">Foo bar</a>')

        self.assertProcesses('[file http://example.org/naked-girl.jpg]', '<img src="http://example.org/naked-girl.jpg" alt="" title="">')

        self.assertProcesses(
            '[youtube dQw4w9WgXcQ]',
            '<div class="g-video"><iframe width="100%" height="100%" src="//www.youtube.com/embed/dQw4w9WgXcQ?wmode=transparent" frameborder="0" allowfullscreen></iframe></div>'
        )

        self.assertProcesses(
            '[vimeo 17687260]',
            '<div class="g-video"><iframe src="//player.vimeo.com/video/17687260?title=0&amp;byline=0&amp;portrait=0" width="560" height="320" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe></div>'
        )

        self.assertProcesses(
            '[smotri v2608403fd41]',
            '<div class="g-video"><object id="smotriComVideoPlayer" classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" width="100%" height="100%"><param name="movie" value="//pics.smotri.com/player.swf?file=v2608403fd41&autoStart=false&str_lang=rus&xmlsource=http%3A%2F%2Fpics%2Esmotri%2Ecom%2Fcskins%2Fblue%2Fskin%5Fcolor%2Exml&xmldatasource=http%3A%2F%2Fpics.smotri.com%2Fcskins%2Fblue%2Fskin_ng.xml" /><param name="allowScriptAccess" value="always" /><param name="allowFullScreen" value="true" /><param name="bgcolor" value="#ffffff" /><embed name="smotriComVideoPlayer" src="//pics.smotri.com/player.swf?file=v2608403fd41&autoStart=false&str_lang=rus&xmlsource=http%3A%2F%2Fpics%2Esmotri%2Ecom%2Fcskins%2Fblue%2Fskin%5Fcolor%2Exml&xmldatasource=http%3A%2F%2Fpics.smotri.com%2Fcskins%2Fblue%2Fskin_ng.xml" quality="high" allowscriptaccess="always" allowfullscreen="true" wmode="window"  width="100%" height="100%" type="application/x-shockwave-flash"></embed></object></div>'
        )

        self.assertProcesses(
            '[video https://coub.com/view/11gpm]',
            '<div class="g-video"><iframe src="//coub.com/embed/11gpm?muted=false&autostart=false&originalSize=false&hideTopBar=false&startWithHD=false" allowfullscreen="true" frameborder="0" width="100%" height="100%"></iframe></div>',
        )

        self.assertProcesses('[ nbsp ]', '&nbsp;')
        self.assertProcesses('adc[ nbsp ]qwe', 'adc&nbsp;qwe')
        self.assertProcesses(' [nbsp]fdf', ' &nbsp;fdf')
        self.assertProcesses(' [nbsp][nbsp]fdf', ' &nbsp;&nbsp;fdf')

    def test_bb_url(self):
        self.assertProcesses('[url http://www.irk.ru]IRK.ru[/url]', '<a href="http://www.irk.ru">IRK.ru</a>')
        self.assertProcesses('[url http://www.irk.ru/foo--bar/]IRK.ru[/url]', '<a href="http://www.irk.ru/foo--bar/">IRK.ru</a>')
        self.assertProcesses('[url https://irk.ru/foo--bar/]IRK.ru[/url]', '<a href="https://irk.ru/foo--bar/">IRK.ru</a>')
        # ссылка на внешний сайт
        self.assertProcesses('[url http://example.org]test[/url]', '<a href="http://example.org" target="_blank" rel="noopener">test</a>')
        self.assertProcesses('[url http://example.org][b]Bold[/b][/url]', '<a href="http://example.org" target="_blank" rel="noopener"><strong>Bold</strong></a>')
        # Обработка cosmetics внутри тега
        self.assertProcesses(u'[url http://example.org]2012--2014[/url]', u'<a href="http://example.org" target="_blank" rel="noopener">2012—2014</a>')

        gp = create_picture()

        before = processor.format('[url http://example.org][image {0}][/url]'.format(gp.id))
        self.assertIn('<img', before)

    def test_quotes(self):
        self.assertProcesses(u'"hello"', u'«hello»')
        self.assertProcesses(u'"hello""', u'«hello»&quot;')
        self.assertProcesses(u'"hello', u'&quot;hello')
        self.assertProcesses(u'"hello "dammit" world"', u'«hello „dammit“ world»')
        self.assertProcesses(u'Hi, my name is a "Slim" Sheady', u'Hi, my name is a «Slim» Sheady')

        self.assertProcesses(u'"[url http://example.org]Test[/url]"', u'«<a href="http://example.org" target="_blank" rel="noopener">Test</a>»')
        self.assertProcesses(u'"[url http://example.org]Test "not" test[/url]"', u'«<a href="http://example.org" target="_blank" rel="noopener">Test „not“ test</a>»')
        self.assertProcesses(u'"[url http://example.org]Test «not» test[/url]"', u'«<a href="http://example.org" target="_blank" rel="noopener">Test „not“ test</a>»')
        self.assertProcesses(u'"[b][i]How «[url http://www.example.org]old[/url]» is that shit?! [/i][/b]" ',
            u'«<strong><em>How „<a href="http://www.example.org" target="_blank" rel="noopener">old</a>“ is that shit?! </em></strong>» ')

    def test_cosmetic(self):
        self.assertProcesses(u'С 2010--2011 года ведется разработка типографа', u'С 2010—2011 года ведется разработка типографа')

    def test_linkify(self):
        self.assertProcesses('http://example.org', '<a href="http://example.org" rel="nofollow">http://example.org</a>')
        # почему-то эта строка не работает
        # self.assertProcesses(u'http://тест.рф', u'<a href="http://тест.рф" rel="nofollow">http://тест.рф</a>')
        self.assertProcesses('<img src="http://example.org">', '&lt;img src=&quot;http://example.org&quot;&gt;')
        self.assertProcesses('<img src=\'http://example.org\'>', '&lt;img src=&#39;http://example.org&#39;&gt;')
        self.assertProcesses('<a href="http://example.org">', '&lt;a href=&quot;http://example.org&quot;&gt;')
        self.assertProcesses('<a href=\'http://example.org\'>', '&lt;a href=&#39;http://example.org&#39;&gt;')

        self.assertProcesses(u'www.i38.ru, www.irk.ru и www.baikal24.ru',
            u'<a href="http://www.i38.ru" rel="nofollow">www.i38.ru</a>, <a href="http://www.irk.ru" rel="nofollow">www.irk.ru</a> и <a href="http://www.baikal24.ru" rel="nofollow">www.baikal24.ru</a>')

    def test_image(self):
        """BB-код [image]"""

        gp = create_picture()

        result = processor.format('[image {0.id}]'.format(gp))
        html = html_fromstring(result)
        self.assertTrue(html.findall('img'), msg='Вывод изображения')
        self.assertFalse(html.find_class('j-irk-tour3d-show'))

        result = processor.format('[image {0.id} center]'.format(gp))
        html = html_fromstring(result)
        self.assertTrue(html.find_class('g-float-center'), msg='Выравнивание по центру')

        result = processor.format('[image {0.id} right]'.format(gp))
        html = html_fromstring(result)
        self.assertTrue(html.find_class('g-float-right'), msg='Выравнивание вправо')

        result = processor.format('[image {0.id} 3d_tour=http://irkutskoil.ml/]'.format(gp))
        html = html_fromstring(result)
        self.assertTrue(html.find_class('b-3dtour-image-container'), msg='3D тур')

    def test_images(self):
        """Проверка BB-кода [images]"""

        gallery_pictures = G(GalleryPicture, n=3)

        result = processor.format('[images {0.id},{1.id},{2.id}]'.format(*gallery_pictures))
        html = html_fromstring(result)
        self.assertEqual(3, len(html.findall('figure')), msg='Вывод изображений')

        # Пробелы между идентификаторами
        result = processor.format('[images {0.id},  {1.id},  {2.id} ]'.format(*gallery_pictures))
        html = html_fromstring(result)
        self.assertEqual(3, len(html.findall('figure')), msg='Вывод изображений')

    def test_images_when_image_not_exist(self):
        """Проверка BB-кода [images], когда передано несуществующее изображение"""

        gallery_pictures = G(GalleryPicture, n=2)

        result = processor.format('[images {0.id},100500,{1.id}]'.format(*gallery_pictures))
        html = html_fromstring(result)

        self.assertEqual(2, len(html.findall('figure')), msg='Вывод изображений')

    def test_card(self):
        """BB-код для вставки твита"""

        html = "<blockquote class=\"twitter-tweet\"><p>Happy 50th anniversary to the Wilderness Act! Here's a great "\
               "wilderness photo from<a href=\"https://twitter.com/YosemiteNPS\">@YosemiteNPS</a>.</p>"\
               "<a href=\"https://twitter.com/hashtag/Wilderness50?src=hash\">#Wilderness50</a></blockquote>"\
               "<script async src=\"//platform.twitter.com/widgets.js\" charset=\"utf-8\"></script>"

        G(TweetEmbed, id=558465674952331265, html=html)
        self.assertProcesses('[card https://twitter.com/mod_russia/status/558465674952331265]', html)

        self.assertProcesses('[card https://twitter.com/mod_russia/status/failed]', '')

        self.assertProcesses('[card broken_url;asd;lfkjwqerxzcvm123]', '')

    def test_cards(self):
        self.assertProcesses('[cards 1][/cards]', '')
        self.assertProcesses('[cards 1][h2]Header[/h2]Some\n\nAnother[/cards]',
            '<div class="material-card" data-index="1"><h2>Header</h2><p>Some</p>\n\n<p>Another</p></div>')
        self.assertProcesses('[cards 1][h3]Header[/h3][/cards]',
            '<div class="material-card" data-index="1"><h3>Header</h3></div>')
        self.assertProcesses('[cards 1]\n[h3]Header[/h3]\n[/cards]',
            '<div class="material-card" data-index="1"><h3>Header</h3></div>')
        self.assertProcesses('[cards]\n[h3]Header[/h3] \n[/cards]',
            '<div class="material-card" data-index=""><h3>Header</h3></div>')
        self.assertProcesses('[cards]\n[h3]Header[/h3]some[/cards]',
            '<div class="material-card" data-index=""><h3>Header</h3><p>some</p></div>')

    def test_ref(self):
        """BB-код для вставки выноски"""

        self.assertProcesses('[ref][/ref]', '')
        self.assertProcesses('[ref]   [/ref]', '')

        self.assertProcesses(
            '[ref]lorem ipsum[/ref]',
            '<div class="g-reference"><div class="g-reference-content">lorem ipsum</div></div>'
        )
        self.assertProcesses(
            '[ref IRK.RU]lorem ipsum[/ref]',
            '<div class="g-reference"><div class="g-reference-content">lorem ipsum<span class="g-reference-source">IRK.RU</span></div></div>'
        )
        self.assertProcesses(
            '[ref IRK.RU http://www.irk.ru]lorem ipsum[/ref]',
            '<div class="g-reference"><div class="g-reference-content">lorem ipsum<a href="http://www.irk.ru" class="g-reference-source">IRK.RU</a></div></div>'
        )
        self.assertProcesses(
            u'[ref IRK.RU http://www.irk.ru ]Русский текст[/ref]',
            u'<div class="g-reference"><div class="g-reference-content">Русский текст<a href="http://www.irk.ru" class="g-reference-source">IRK.RU</a></div></div>'
        )

    def test_smiles_with_square_brackets(self):
        sample = textwrap.dedent(u'''
        эх...диванные разошлись. *ROFL*
        Ну попробуйте собрать "первичный" отсев после зимы, очистить его от окурков, мусора, складировать его где-то (диванщики даже не в курсе объемов отсева, высыпаемого на улицы города) на площадях, сравнимых с футбольными полями (и не одним), а потом хранить его в течении весны, лета, зимы и чтобы он не пылил на близлежащие территории.диван
        Не надо сравнивать "загнивающую Европу" с Россией.
        Конечно, если диванные найдут площади под очистку и хранение вторичного отсева - да хоть десятками лет подряд один и тот же отсев будут использовать на дорогу.
        А если соль не сыпать - то и бордюры будут стоять десятилетиями, и обувь не одному сезону носиться, и машины гнить перестанут и т.п.
        Но у нас на посыпанной и засоленной дороге диванные умудряются в ДТП попадать. Скоростной режим это не для них в ПДД указано.
        "Минуснуть" мой коммент легко - жду конкретных предложений. Особенно от представителей конторы "на три буквы  =-O ОНФ  :-[
        ''')
        result = textwrap.dedent(u'''
        эх…диванные разошлись. <img title="ржунимагу" src="/static/img/smiles/bj.gif" alt="ржунимагу" />
        Ну попробуйте собрать «первичный» отсев после зимы, очистить его от окурков, мусора, складировать его где-то (диванщики даже не в курсе объемов отсева, высыпаемого на улицы города) на площадях, сравнимых с футбольными полями (и не одним), а потом хранить его в течении весны, лета, зимы и чтобы он не пылил на близлежащие территории.диван
        Не надо сравнивать «загнивающую Европу» с Россией.
        Конечно, если диванные найдут площади под очистку и хранение вторичного отсева - да хоть десятками лет подряд один и тот же отсев будут использовать на дорогу.
        А если соль не сыпать - то и бордюры будут стоять десятилетиями, и обувь не одному сезону носиться, и машины гнить перестанут и т.п.
        Но у нас на посыпанной и засоленной дороге диванные умудряются в ДТП попадать. Скоростной режим это не для них в ПДД указано.
        «Минуснуть» мой коммент легко - жду конкретных предложений. Особенно от представителей конторы &quot;на три буквы  <img title="в шоке" src="/static/img/smiles/ai.gif" alt="в шоке" /> ОНФ  <img title="смущаюсь" src="/static/img/smiles/ah.gif" alt="смущаюсь" />
        ''')

        self.assertProcesses(sample, result)

    def assertProcesses(self, before, after):
        self.assertEqual(processor.format(before), after)

    def create_picture(self):
        image = DjangoFile(open(find('img/irkru.png')))
        picture = G(Picture, image=image)

        return G(GalleryPicture, picture=picture)


class ZenProcessorTest(UnitTestBase):
    def test_image(self):
        gp = create_picture()

        result = zen_processor.format('[image {0.id}]'.format(gp))
        html = html_fromstring(result)
        self.assertEqual('figure', html.tag)
        self.assertTrue(html.findall('img'))
        self.assertTrue(html.findall('figcaption'))

    def test_remove_html_tags(self):
        content = '''
            [video https://youtu.be/ZGbx8qKVszI]

            <iframe src="https://www.podbean.com/media/player/7uyuy-6c1854?from=site&skin=1&share=1&fonts=Helvetica&auto=0&download=0"
            height="100" width="100%" frameborder="0" scrolling="no" data-name="pb-iframe-player"></iframe>
        '''

        content = bleach.clean(content, strip=True)
        result = zen_processor.format(content)

        self.assertNotIn('youtu', result)
        self.assertNotIn('iframe', result)
