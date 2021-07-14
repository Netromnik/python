# -*- coding: utf-8 -*-

import logging
import os.path
import traceback
import random
import re
import urlparse
from shutil import copyfile

import six
from PIL import Image
from django.conf import settings
from django.core.urlresolvers import NoReverseMatch
from django.template.loader import render_to_string, get_template
from django.utils.html import linebreaks
from django.template.defaultfilters import linebreaksbr
from sorl.thumbnail.base import ThumbnailException
from sorl.thumbnail.main import DjangoThumbnail

from irk.afisha.models import Event
from irk.gallery.models import GalleryPicture, Picture
from irk.news.models import BaseMaterial
from irk.utils.decorators import deprecated
from irk.utils.embed_widgets import TwitterEmbedWidget, VkVideoEmbedWidget, InstagramEmbedWidget
from irk.utils.helpers import get_object_or_none
from irk.utils.models import TweetEmbed, VkVideoEmbed, InstagramEmbed
from irk.utils.text.formatters.base import Formatter

logger = logging.getLogger(__name__)

# Adapted from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
# Changed to only support one level of parentheses, since it was failing catastrophically on some URLs.
# See http://www.regular-expressions.info/catastrophic.html
url_re = re.compile(
    r'(?im)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\([^\s()<>]+\))+(?:\([^\s()<>]+\)|[^\s`!()\[\]{};:\'".,<>?]))')

# For the URL tag, try to be smart about when to append a missing http://. If the given link looks like a domain,
# add a http:// in front of it, otherwise leave it alone (since it may be a relative path, a filename, etc).
_domain_re = re.compile(
    r'(?im)(?:www\d{0,3}[.]|[a-z0-9.\-]+[.](?:com|net|org|edu|biz|gov|mil|info|io|name|me|tv|us|uk|mobi|ru))')

_image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

_https_url_prefix = 'https://' if settings.FORCE_HTTPS else 'http://'

# HTML с кодами встраиваемых видео
YOUTUBE_EMBED_HTML = u'<div class="g-video"><iframe width="100%" height="100%" src="//www.youtube.com/embed/{0}?wmode=transparent" frameborder="0" allowfullscreen></iframe></div>'
VIMEO_EMBED_HTML = u'<div class="g-video"><iframe src="//player.vimeo.com/video/{0}?title=0&amp;byline=0&amp;portrait=0" width="560" height="320" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe></div>'
SMOTRI_EMBED_HTML = u'<div class="g-video"><object id="smotriComVideoPlayer" classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" width="100%" height="100%"><param name="movie" value="//pics.smotri.com/player.swf?file={0}&autoStart=false&str_lang=rus&xmlsource=http%3A%2F%2Fpics%2Esmotri%2Ecom%2Fcskins%2Fblue%2Fskin%5Fcolor%2Exml&xmldatasource=http%3A%2F%2Fpics.smotri.com%2Fcskins%2Fblue%2Fskin_ng.xml" /><param name="allowScriptAccess" value="always" /><param name="allowFullScreen" value="true" /><param name="bgcolor" value="#ffffff" /><embed name="smotriComVideoPlayer" src="//pics.smotri.com/player.swf?file={0}&autoStart=false&str_lang=rus&xmlsource=http%3A%2F%2Fpics%2Esmotri%2Ecom%2Fcskins%2Fblue%2Fskin%5Fcolor%2Exml&xmldatasource=http%3A%2F%2Fpics.smotri.com%2Fcskins%2Fblue%2Fskin_ng.xml" quality="high" allowscriptaccess="always" allowfullscreen="true" wmode="window"  width="100%" height="100%" type="application/x-shockwave-flash"></embed></object></div>'
VKONTAKTE_EMBED_HTML = u'<div class="g-video"><iframe src="{0}" width="100%" height="100%" frameborder="0"></iframe></div>'
COUB_EMBED_HTML = u'<div class="g-video"><iframe src="//coub.com/embed/{0}?muted=false&autostart=false&originalSize=false&hideTopBar=false&startWithHD=false" allowfullscreen="true" frameborder="0" width="100%" height="100%"></iframe></div>'
FACEBOOK_EMBED_SCRIPT = u"""<script>(function(d,s,id) { var js, fjs = d.getElementsByTagName(s)[0];  if (d.getElementById(id)) return;  js = d.createElement(s); js.id = id;  js.src = "//connect.facebook.net/ru_RU/sdk.js#xfbml=1&version=v2.3";  fjs.parentNode.insertBefore(js, fjs);}(document, 'script', 'facebook-jssdk'));</script>"""
FACEBOOK_EMBED_HTML = u'<div class="g-video"><div class="fb-video" data-href="{0}"></div></div>'
YANDEX_EMBED_HTML = u'<div class="g-video"><iframe width="100%" height="100%" src="https://frontend.vh.yandex.ru{0}?from=partner&mute=1&autoplay=1&tv=0&no_ad=false&loop=true&play_on_visible=true" allow="autoplay; fullscreen; accelerometer; gyroscope; picture-in-picture; encrypted-media" frameborder="0" scrolling="no" allowfullscreen></iframe></div>'


def article_element(original_function):
    """Декоратор, оборачивает вывод в див с классом article-element"""

    TEMPLATE = u'<div class="article-element article-element_wide">{0}</div>'

    def new_function(*args, **kwargs):
        html = original_function(*args, **kwargs)
        return TEMPLATE.format(html) if html else html
    return new_function


def url_formatter(name, value, options, parent, context):
    """BB код [url]"""

    # TODO: replace html entities from options[0]

    try:
        href = options[0]
    except IndexError:
        href = value

    up = urlparse.urlparse(href)
    if up.netloc.endswith('irk.ru'):
        return u'<a href="%s">%s</a>' % (href, value)

    return u'<a href="%s" target="_blank" rel="noopener">%s</a>' % (href, value)


def email_formatter(name, value, options, parent, context):
    """BB код [email]"""

    try:
        href = options[0]
    except IndexError:
        href = value

    return u'<a href="mailto:%s">%s</a>' % (href, value)


def image_formatter_disabled(name, value, options, parent, context):
    """BB код [image]

    Примеры использования::
        [image 12345], где 12345 идентификатор объекта :class:`irk.gallery.models.GalleryPicture`
        [image 12345 center] - изображение с выравниванием по центру
        [image 12345 right] - изображение с выравниванием по правому краю
        [image 12345 center 625x1000 stretch] - изображение с выравниванием по центру
                                                с кастомным масшатабированием (625х1000) и растягиванием блюром
        [image 12345 3d_tour=http://irkutskoil.ml/] - изображение с сылкой на 3D тур
    """

    from irk.utils.text.processors.only_url import processor

    thumbnail_options = {'x': False}

    # Получение url 3D тура
    link_3d = None
    for option in options:
        if option.startswith('3d_tour='):
            link_3d = option.replace('3d_tour=', '')
            options.remove(option)
            break

    pk = options[0]
    try:
        align = options[1]
        if align not in ('left', 'center', 'right'):
            raise ValueError()
    except (ValueError, IndexError):
        align = 'center'

    # Размер изображений по-умолчанию для текстов, обрабатываемых типографом
    size = (705, 1000)
    is_scalable = False
    image_options = context.get('image', False)
    if image_options:
        # Опции разделяются символом 'x'
        image_options = image_options.split('x')
        try:
            size = (int(image_options[0]), int(image_options[1]))
            if 'stretch' in image_options:
                thumbnail_options['stretch'] = 1
            if 'scalable' in image_options:
                is_scalable = True
        except (IndexError, TypeError):
            pass

    try:
        if pk.isdigit():
            file_ = GalleryPicture.objects.select_related('picture').get(pk=pk)
            thumbnail_options['x'] = file_.picture.watermark
            thumb = DjangoThumbnail(file_.picture.image, size, opts=thumbnail_options)
            title = file_.picture.title
        else:
            try:
                thumb = DjangoThumbnail(pk, size, opts=thumbnail_options)
                title = ''
            except ThumbnailException:
                logger.exception("Can't create thumbnail for {}".format(pk))
                return ''

        params = {
            'src': unicode(thumb),
            # Обработка тега [url] в название изображения
            'title': processor.format(title, replace_links=False),
            'align': align,
            'width': thumb.width(),
            'height': thumb.height(),
            'link_3d': link_3d
        }

        # Задана возможность масштабирования изображений
        if is_scalable and 'file_' in vars():
            # Возможность масштабирования добавляется только для изображений у которых размеры больше запрашиваемых
            src_image = file_.picture.image
            if src_image.width > thumb.width() or src_image.height > thumb.height():
                params.update({
                    'big_src': src_image.url,
                    'big_width': src_image.width,
                    'big_height': src_image.height,
                })

        result = render_to_string('bb_codes/image.html', params)
        # Удаляем символы переноса строки, т.к. при выводе типограф применяет фильтр linebreaks
        return result.replace('\n', '')

    except (GalleryPicture.DoesNotExist, ThumbnailException):
        return ''


class DjangoGifThumbnail(DjangoThumbnail):

    def _do_generate(self):
        copyfile(self.source, self.dest)


class ImageFormatter(Formatter):
    template = 'bb_codes/image.html'
    default_image_size = (705, 1000)

    def render(self):
        image_opts = self.parse_image_options()
        context = self.prepare_context(image_opts)
        result = render_to_string(self.template, context) if context else ''

        # Удаляем символы переноса строки, т.к. при выводе типограф применяет фильтр linebreaks
        return result.replace('\n', '')

    def parse_image_options(self):
        opts = self.context.get('image', None)
        if not opts:
            return {
                'size': self.default_image_size,
                'stretch': False,
                'scalable': False,
            }

        # Опции разделяются символом 'x'
        opts = opts.split('x')
        return {
            'size': (opts[0], opts[1]),
            'stretch': 'stretch' in opts,
            'scalable': 'scalable' in opts,
        }

    def is_animated_gif(self, image):
        """
        Является ли изображение анимированным GIF

        image может быть объектом типа Image или строкой [image img/uploads/..]
        """
        if isinstance(image, six.string_types):  # py2 & py3
            # todo: в image может передаваться вредоносная строка, надо бы фильтровать
            filename = image
        else:
            filename = image.name

        filename = os.path.join(settings.MEDIA_ROOT, filename)

        if filename.endswith('.gif'):
            im = Image.open(filename)
            frames_cnt = 0
            try:
                while 1:
                    frames_cnt += 1
                    im.seek(im.tell() + 1)
            except EOFError:
                pass
            return frames_cnt > 1
        return False

    def prepare_context(self, image_opts):
        source = self.options[0]
        picture = self.get_picture(source)
        if picture:
            image = picture.image
            thumb_opts = self.get_thumb_options(image_opts, picture)
        else:
            image = source
            thumb_opts = self.get_thumb_options(image_opts)

        if self.is_full():
            # если у нас фотка во всю ширину
            image_opts['size'] = (1920, 1300)

        if self.is_animated_gif(image):
            thumb = self.get_gif_thumb(image, (0, 0))  # не ресайзить
        else:
            thumb = self.get_thumb(image, image_opts['size'], thumb_opts)

        if not thumb:
            return None

        context = {
            'src': unicode(thumb),
            'title': picture.title if picture else '',
            'align': self.get_align(),
            'full': self.is_full(),
            'upscale': self.is_upscale(),
            'width': thumb.width(),
            'height': thumb.height(),
            'link_3d': self.get_link_3d(),
        }

        if image_opts['scalable'] and picture:
            img = picture.image
            if (thumb.width(), thumb.height()) < (img.width, img.height):
                context.update({
                    'big_src': img.url,
                    'big_width': img.width,
                    'big_height': img.height,
                })

        return context

    def get_picture(self, source):
        if source.isdigit():
            return Picture.objects.filter(gallerypicture__pk=source).first()

    def get_thumb_options(self, image_opts, picture=None):
        thumb_opts = {
            'x': picture.watermark if picture is not None else False,
        }

        if image_opts['stretch']:
            thumb_opts['stretch'] = 1

        return thumb_opts

    def get_thumb(self, image, size, opts):
        try:
            thumb = DjangoThumbnail(image, size, opts=opts)
            return thumb
        except ThumbnailException as exc:
            logger.error("Can't create thumbnail for %s: %s", image, exc)

    def get_gif_thumb(self, image, size):
        try:
            thumb = DjangoGifThumbnail(image, size, extension='gif')
            return thumb
        except ThumbnailException as exc:
            logger.error("Can't create thumbnail for %s: %s", image, exc)

    def get_link_3d(self):
        link_3d = None
        for option in self.options:
            if option.startswith('3d_tour='):
                link_3d = option.replace('3d_tour=', '')
                break

        return link_3d

    def get_align(self):
        try:
            align = self.options[1]
            if align not in ('left', 'center', 'right'):
                align = ''
        except (ValueError, IndexError):
            align = ''

        return align

    def is_full(self):
        return 'full' in self.options

    def is_upscale(self):
        return 'upscale' in self.options


def images_formatter(name, value, options, parent, context):
    """
    BB код [images]. Используется для вывода нескольких картинок в виде слайдера.

    Примеры использования:
        [images 113322,445566,778899]
    """

    # Идентификаторы через запятую с пробелом
    if len(options) > 1:
        options = [''.join(options)]
    elif len(options) < 1:
        return ''

    id_list = options[0].split(',')

    size = context.get('gallery', '620x460')

    pictures = []
    for pk in id_list:
        try:
            pk = int(pk)
            gallery_picture = GalleryPicture.objects.select_related('picture').get(pk=pk)
            pictures.append(gallery_picture.picture)
        except ValueError:
            logger.info('Invalid picure id in `images` tag with options: %s', options)
        except GalleryPicture.DoesNotExist:
            logger.info('GalleryPicture id=%s does not exist', pk)
            continue

    result = render_to_string('bb_codes/images.html', {
        'pictures': pictures,
        'size': size,
    })
    # Удаляем символы переноса строки, т.к. при выводе типограф применяет фильтр linebreaks
    return result.replace('\n', '')


def diff_formatter(name, value, options, parent, context):
    """
    BB код [diff]. Используется для вывода слайдера до - после.

    Примеры использования:
        [diff 113322,445566]
        [diff 113322, 445566 before="2009" after="2015"]
    """

    # Вырезаем именнованные параметры
    params = {}
    for item in options[:]:
        if '=' in item:
            key, value = item.split('=', 1)
            params[key] = value.strip('"\'')
            options.remove(item)

    before_label = params.get('before', '')
    after_label = params.get('after', '')

    # Идентификаторы через запятую с пробелом
    if len(options) > 1:
        options = [''.join(options)]
    elif len(options) < 1:
        return ''

    id_list = options[0].split(',')

    pictures = []
    for pk in id_list:
        try:
            gallery_picture = GalleryPicture.objects.select_related('picture').get(pk=pk)
            pictures.append(gallery_picture.picture)
        except GalleryPicture.DoesNotExist:
            logger.warning('Does not exist object with pk {}'.format(pk))
            continue

    if len(pictures) < 2:
        return ''

    result = render_to_string('bb_codes/diff_slider.html', {
        'picture_1': pictures[0],
        'picture_2': pictures[1],
        'before_label': before_label,
        'after_label': after_label,
    })
    # Удаляем символы переноса строки, т.к. при выводе типограф применяет фильтр linebreaks
    return result.replace('\n', '')


def audio_formatter(name, value, options, parent, context):
    """ВВ код [audio]

    Используется для вставки плеера аудиофайла. Например:
        [audio 1489]
        [audio img/site/uploads/2018/12/75b2b0ad4b7ee0a470240c8f8b091773e142f4a5.mp3]
        [audio http://example.com/song.mp3]Какой-то дополнительный тайтл[/audio]
    """
    src = options[0]
    title = value or ''

    if src.isdecimal():
        from irk.uploads.models import Upload
        try:
            obj = Upload.objects.get(id=src)
        except Upload.DoesNotExist:
            return ''
        src = obj.file.url
        title = value if value else obj.title

    elif not src.startswith(('http://', 'https://')):
        # относительный урл - от корня media
        src = settings.MEDIA_URL + src

    return render_to_string('bb_codes/audio.html', {
        'id': random.randint(1, 999999),
        'src': src,
        'title': title,
    })


def file_formatter(name, value, options, parent, context):
    """BB код [file]

    Есть два варианта использования кода:
        - передается ссылка
        - передается идентификатор объекта модели :class:`irk.pages.models.File`
    """

    href = options[0]

    try:
        align = ' align={0}'.format(options[1])
    except IndexError:
        align = ''

    size = ''

    if href.isdigit():
        from irk.pages.models import File
        try:
            obj = File.objects.get(id=href)
        except File.DoesNotExist:
            # TODO: logger.warning()
            return ''

        href = obj.file.url
        try:
            image = Image.open(obj.file.path)
        except IOError:
            return ''
        size = ' style="width:{0}px;height:{1}px;"'.format(*image.size)

    value = value or ''

    name, ext = os.path.splitext(href)
    if ext in _image_extensions:
        return u'<img src="{href}" alt="{title}" title="{title}"{align}{size}>'.format(href=href, title=value,
                                                                                       align=align, size=size)
    return u'<a href="{href}">{title}</a>'.format(href=href, title=value)


@deprecated  # Используется BB код [video], эта функция оставлена для обратной совместимости
def youtube_formatter(name, value, options, parent, context):
    """BB код [youtube]"""

    return YOUTUBE_EMBED_HTML.format(options[0])


@deprecated  # Используется BB код [video], эта функция оставлена для обратной совместимости
def vimeo_formatter(name, value, options, parent, context):
    """BB код [vimeo]"""

    return VIMEO_EMBED_HTML.format(options[0])


@deprecated  # Используется BB код [video], эта функция оставлена для обратной совместимости
def smotricom_formatter(name, value, options, parent, context):
    """BB код [smotri]"""

    return SMOTRI_EMBED_HTML.format(options[0])


@article_element
def video_formatter(name, value, options, parent, context):
    """BB код [video]"""

    url = urlparse.urlparse(options[0])
    location = url.netloc
    params = urlparse.parse_qs(url.query)

    try:
        if 'youtube.com' in location:
            return YOUTUBE_EMBED_HTML.format(params['v'][0])
        elif 'youtu.be' in location:
            return YOUTUBE_EMBED_HTML.format(url.path.lstrip('/'))
        elif 'vimeo.com' in location:
            return VIMEO_EMBED_HTML.format(url.path.lstrip('/'))
        elif 'vk.com' in location or 'vkontakte.ru' in location:
            widget = VkVideoEmbedWidget(content='')
            entry_id = widget.get_entry_id(url.geturl())
            embed = get_object_or_none(VkVideoEmbed, pk=entry_id)
            if not embed:
                logger.error('Not found embed video widget for id: {}'.format(entry_id))
                return ''
            html = embed.html.replace('http://', '//')
            return VKONTAKTE_EMBED_HTML.format(html)
        elif 'smotri.com' in location:
            return SMOTRI_EMBED_HTML.format(params['id'][0])
        elif 'coub.com' in location:
            return COUB_EMBED_HTML.format(os.path.basename(url.path))
        elif 'facebook.com' in location:
            return FACEBOOK_EMBED_SCRIPT + FACEBOOK_EMBED_HTML.format(url.path)
        elif 'frontend.vh.yandex.ru' in location:
            return YANDEX_EMBED_HTML.format(url.path)

        raise ValueError('Unknown video URL for BB code [video]')

    except (KeyError, IndexError, ValueError):
        logger.exception('Can\'t parse BB code {0} with that options: {1}'.format(name, ', '.join(options)))
        return ''


@article_element
def card_formatter(name, value, options, parent, context):
    """BB код [card <url>] для вставки виджетов Твиттера и других"""

    url = options[0]
    location = urlparse.urlparse(url).netloc

    if 'twitter.com' in location:
        widget = TwitterEmbedWidget(content='')
        entry_id = widget.get_entry_id(url)
        embed = TweetEmbed.objects.filter(pk=entry_id).first()
        if not embed:
            logger.error('Not found tweet embed for id: {}'.format(entry_id))
            return ''
        return embed.html
    elif any(key in location for key in ['instagram', 'instagr']):
        widget = InstagramEmbedWidget(content='')
        entry_id = widget.get_entry_id(url)  # ex: B-erIuIJ_qK
        embed = InstagramEmbed.objects.filter(pk=entry_id).first()
        if not embed:
            logger.error('Not found instagram embed for id: {}'.format(entry_id))
            return ''
        return embed.html
    else:
        return ''


@article_element
def cards_formatter(name, value, options, parent, context):
    """
    BB код [cards <number>] для вставки карточек
    Параметры:
        number - номер карточки
    Примеры использования:
        [cards 1][h2]Заголовок[/h2]Текст[/cards]
        [cards 2]
            [h2]Заголовок[/h2]
            Текст
        [/cards]
    """

    try:
        number = options[0]
    except IndexError:
        number = ''

    # уберем переносы, чтобы не вставлялись лишние br после заголовка
    value = re.sub(r'^\s*(<h\d>.*</h\d>)\s*', r'\1', value)

    # обычно linebreaks делается в do_typograf, но в случае карточек это
    # ломает разметку, поэтому заворачиваем текст в параграфы прямо тут
    value = linebreaks(value)

    # вынесем заголовок за параграф
    value = re.sub(r'^<p>(<h\d>.*</h\d>)', r'\1<p>', value)

    # вырежем пустые параграфы
    value = value.replace('<p></p>', '').strip()

    if value:
        return u'<div class="material-card" data-index="{}">{}</div>'.format(number, value)
    else:
        return ''

def ucard_formatter(name, value, options, parent, context):
    """
    ВВ-код [ucard supheader="xx" title="yy"] - универсальная карточка
    """
    if not value:
        return ''

    options_string = ' '.join(options)

    result = ''
    supheader = ''
    match = re.search(r'supheader="([^"]*)"', options_string)
    if match:
        supheader = match.group(1)
        result = u'<div class="ucard__date">{}</div>'.format(supheader)

    title = ''
    match = re.search(r'title="(.*?)"', options_string)
    if match:
        title = match.group(1)
        result += u'<h2 class="ucard__title">{}</h2>'.format(title)

    value = linebreaks(value.lstrip().rstrip(), autoescape=False)

    result = result + u'<div class="ucard__content">{}</div>'.format(value)

    return u'<div class="ucard">{}</div>'.format(result)



def ref_formatter(name, value, options, parent, context):
    """
    BB-код [ref <source> <href>]<content>[/ref] для вставки сноски в текст
    Параметры:
        source - источник информации
        href - ссылка на источник
        content - содержание сноски

    Примеры использования:
        [ref]Джон Барлоу утверждает...[/ref]
        [ref IRK.RU]Джон Барлоу утверждает...[/ref]
        [ref IRK.RU http://irk.ru]Джон Барлоу утверждает...[/ref]
    """

    if not value.strip():
        return ''

    try:
        source = options[0]
    except IndexError:
        source = None

    try:
        href = options[1]
    except IndexError:
        href = None

    result = [u'<div class="g-reference"><div class="g-reference-content">{}'.format(value)]
    if href and source:
        result.append(u'<a href="{}" class="g-reference-source">{}</a>'.format(href, source))
    elif source:
        result.append(u'<span class="g-reference-source">{}</span>'.format(source))
    result.append(u'</div></div>')

    return u''.join(result)


def spoiler_formatter(name, value, options, parent, context):
    """
    BB-код [spoiler <name>]<content>[/spoiler] для спойлера
    Параметры:
        name - название спойлера
        content - содержание спойлера

    Примеры использования:
        [spoiler Показать подробнее]Скрытый текст[/spoiler]
        [spoiler small Показать подробнее]Скрытый текст[/spoiler]
    """

    if not value.strip():
        return ''

    small_class = ''
    start_pos = 0

    try:
        if options[0] == 'small':
            small_class = ' small'
            start_pos = 1
    except IndexError:
        pass

    try:
        name = u' '.join(options[start_pos:])
    except IndexError:
        return ''

    return u'<div class="spoiler{}"><details><summary><i>{}</i></summary><div>{}</div></details></div>' \
            .format(small_class, name, value)


def material_formatter(name, value, options, parent, context):
    """
    BB-код [material <id>] для вставки карточки материала в текст

    Параметры:
        id - идентификатор материала

    Примеры использования:
        [material 52111]
        [material 52112]
        [material 52113]
    """

    try:
        material_id = options[0]
    except IndexError:
        return ''

    material = BaseMaterial.objects.filter(pk=material_id).first()
    if not material:
        return ''

    result = render_to_string('bb_codes/material.html', {
        'material': material.cast(),
        'request': {'user_agent': {'is_gadget': False}}
    })
    # Удаляем символы переноса строки, т.к. при выводе типограф применяет фильтр linebreaks
    return result.replace('\n', '')


def ticket_formatter(name, value, options, parent, context):
    """BB код [ticket]"""

    try:
        event_id = int(options[0])
    except ValueError:
        event_id = parse_event_id_from_url(options[0])

    event = Event.objects.filter(pk=event_id).select_related('type').first()
    if not event:
        return ''

    if event.type.alias == 'cinema':
        template = 'afisha/snippets/cinema_buy_button.html'
        metrika = 'cinema_buy_click'
    else:
        template = 'afisha/snippets/buy_button.html'
        metrika = 'afisha_buy_click'
    session = event.nearest_tickets_session()

    context = {
        'additional_class': 'ticket-button',
        'event': event,
        'metrika': metrika,
        'session': session,
        'settings': settings,
    }

    # Удаление переносов строк в шаблоне для того чтобы типограф не превращал их в абзацы
    template_obj = get_template(template)
    result = template_obj.render(context)
    return result.replace('\r', ' ').replace('\n', ' ')


def parse_event_id_from_url(url):
    match = re.search(r'/afisha/\w+/\d+/(\d+)/', url)
    if match:
        return match.group(1)
