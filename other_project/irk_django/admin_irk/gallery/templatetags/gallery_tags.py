# -*- coding: utf-8 -*-

import logging

from django import template
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.db import models

from sorl.thumbnail.base import ThumbnailException
from sorl.thumbnail.main import DjangoThumbnail

from irk.utils.templatetags import parse_arguments

from irk.gallery import settings as app_settings

logger = logging.getLogger(__name__)
register = template.Library()


class GalleryNode(template.Node):
    def __init__(self, gallery, preview=None, image=None, thumb=None, mark_first=False, **kwargs):
        self._gallery = gallery

        self._image = image
        self._preview = preview
        self._thumb = thumb
        self._mark_first = mark_first
        self._template = kwargs.pop('template', None)
        self._css_class = kwargs.pop('class', None)
        self._url = kwargs.pop('url', None)
        self._kwargs = kwargs  # Остальные параметры передаются, как opts DjangoThumbnail для превьюшки

    def get_image(self, obj):
        return obj.image

    def render(self, context):
        gallery = self._gallery.resolve(context)

        image = self._image.resolve(context) if self._image else None
        preview = self._preview.resolve(context) if self._preview else None
        thumb = self._thumb.resolve(context) if self._thumb else None

        thumb_opts = {}
        for k, v in self._kwargs.items():
            if isinstance(v, template.base.FilterExpression):
                thumb_opts[k] = v.resolve(context)
            else:
                thumb_opts[v] = v

        # Размеры превьюшек
        sizes = {
            'image': [int(x) for x in image.split('x')] if image else app_settings.DEFAULT_IMAGE_SIZE,
            'preview': [int(x) for x in preview.split('x')] if preview else app_settings.DEFAULT_PREVIEW_SIZE,
            'thumb': [int(x) for x in thumb.split('x')] if thumb else app_settings.DEFAULT_THUMB_SIZE,
        }

        images = []
        if gallery:
            for item in gallery:
                try:
                    image = DjangoThumbnail(self.get_image(item), sizes['image'])
                    preview = DjangoThumbnail(self.get_image(item), sizes['preview'], opts=thumb_opts)
                    thumb = DjangoThumbnail(self.get_image(item), sizes['thumb'])
                    if hasattr(item, 'watermark'):
                        image_watermark = DjangoThumbnail(self.get_image(item), sizes['image'],
                                                          opts={'x': item.watermark})
                    else:
                        image_watermark = image
                except (ThumbnailException, IOError):
                    # TODO: logging
                    continue

                images.append({
                    'id': item.id,
                    'title': item.alt,
                    'image': image,
                    'preview': preview,
                    'thumb': thumb,
                    'image_watermark': image_watermark
                })

        template_name = self._template.resolve(context) if self._template else 'gallery/gallery_content.html'

        css_class = self._css_class.resolve(context).strip('\'').strip('"') if self._css_class else None

        url = None
        if self._url:
            url = self._url.resolve(context)
            if isinstance(url, models.Model):
                url = url.get_absolute_url()

        template_context = {
            'images': images,
            'mark_first': self._mark_first,
            'css_class': css_class,
            'url': url,
        }

        return render_to_string(template_name, template_context)


@register.tag
def gallery(parser, token):
    """Рендеринг HTML для галереи

    Примеры использования::
        {% gallery news.gallery.main %}
        {% gallery item.gallery.main|slice:"1:" %}

    Три дополнительных параметра устанавливают получаемых размеры изображений::
        - image: большое изображение в галерее
        - thumb: маленькое изображение в галерее
        - preview: маленькое изображение на странице, по клику на которое открывается галерея

    Остальные параметры::
        - mark_first: при указании у первого элемента галереи добавляется класс
        - template: путь до шаблона
        - url: если указан, не выводятся классы для js, ссылки с фотографий ведут на `url` с хэшем,
               идентифицирующим изображение

    Если какие-либо из этих параметров не указаны, используются настройки по умолчанию из 'gallery.settings`
    Значения параметров должны указываться в кавычках!

    Пример::
        {% gallery item.gallery.main_gallery '100x75' thumb='99x88' %}
    """

    bits = token.split_contents()
    mark_first = 'mark_first' in bits
    try:
        bits.pop(bits.index('mark_first'))
    except ValueError:
        pass

    gallery = parser.compile_filter(bits[1])
    args, kwargs = parse_arguments(parser, bits[2:])
    kwargs['mark_first'] = mark_first

    return GalleryNode(gallery, *args, **kwargs)


class GalleryFormNode(template.Node):
    def __init__(self, formset, max_count=None, per_page=None, single=None, nostyle=None):
        self._formset = formset
        self._max_count = max_count
        self._per_page = per_page
        self._single = single
        self._nostyle = nostyle

    def render(self, context):
        formset = self._formset.resolve(context)
        single = self._single.resolve(context) if self._single else False
        max_count = self._max_count.resolve(context) if self._max_count else 8
        per_page = self._per_page.resolve(context) if self._per_page else 4
        nostyle = self._nostyle.resolve(context) if self._nostyle else False

        objects_length = formset.get_queryset().count()

        template_context = {
            'formset': formset,
            'objects_length': objects_length,
            'max': objects_length if objects_length > max_count else max_count,
            'per_page': per_page,
            'upload_data': {'id': 0},
            'nostyle': nostyle,
        }
        template_name = 'gallery/gallery_form_single.html' if single else 'gallery/gallery_form.html'

        return render_to_string(template_name, template_context)


@register.tag
def gallery_form_new(parser, token):
    """Формсет галереи на клиенте

    Первым параметром должен быть объект класса ``gallery.forms.helpers.gallery_formset''

    Дополнительные параметры::
        max_count: максимальное количество форм формсета
        per_page: какое количество форм будет открыто сразу, и какое количество будет добавлять
                  при нажатии на ссылку «Добавить еще»
        single - если True, то отображается всего одна форма

    Примеры использования::
        {% gallery_form_new gallery_formset [single=True] %}
        {% gallery_form_new gallery_formset 8 [single=True] %}
        {% gallery_form_new gallery_formset 8 4 [single=True] %}
    """

    bits = token.split_contents()
    args, kwargs = parse_arguments(parser, bits[1:])

    if not args:
        raise template.TemplateSyntaxError(u'Первым параметром `{% gallery_form_new %}\' должен быть formset галерей')

    return GalleryFormNode(*args, **kwargs)


class GalleryFormsetNode(template.Node):

    def __init__(self, formset, max=8, per_page=4, template=None):
        self.formset = formset
        self.max_items = max
        self.per_page = per_page
        self.template = template

    def render(self, context):
        formset = self.formset.resolve(context)
        gallery = formset.instance
        objects_length = formset.get_queryset().count()

        if gallery.pk:
            upload_data = {
                'gallery_id': gallery.pk
            }
        else:
            upload_data = {
                'content_type_id': gallery.content_type_id,
                'object_id': None,
            }

        template_context = {
            'formset': formset,
            'objects_length': objects_length,
            'max': (max, objects_length, self.max_items),
            'per_page': self.per_page,
            'upload_data': upload_data
        }

        return render_to_string('gallery/forms/multiupload_formset.html', template_context)


@register.tag
def gallery_formset(parser, token):
    """Формсет мультизагрузчика галереи на клиенте

    Первым параметром должен быть объект класса ``gallery.forms.helpers.gallery_formset''

    Дополнительные именованные параметры::
        max: максимальное количество форм формсета
        per_page: какое количество форм будет открыто сразу, и какое количество будет добавлять
                  при нажатии на ссылку «Добавить еще»

    Примеры использования::
        {% gallery_formset gallery_formset  %}
        {% gallery_formset gallery_formset max=8 %}
        {% gallery_formset gallery_formset max=8 per_page=4 %}
    """

    bits = token.split_contents()
    args, kwargs = parse_arguments(parser, bits[1:])

    return GalleryFormsetNode(*args, **kwargs)
