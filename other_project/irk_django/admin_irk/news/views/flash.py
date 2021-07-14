# -*- coding: utf-8 -*-

import datetime

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import View
from sorl.thumbnail.base import ThumbnailException
from sorl.thumbnail.main import DjangoThumbnail

from irk.gallery.forms.helpers import gallery_formset
from irk.news.forms import FlashForm
from irk.news.helpers import twitter_images
from irk.news.helpers.grabbers import FlashVideoPreviewGrabber
from irk.news.models import Flash
from irk.news.permissions import get_flash_moderators, is_flash_moderator
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse
from irk.utils.notifications import tpl_notify


class IndexView(View):
    """Главная народных новостей"""

    main_limit = 20
    title = u'Народные новости'
    sidebar_limit = 10
    sidebar_title = u'Лента ДТП'
    sidebar_url = reverse_lazy('news:flash:index_dtp')

    def post(self, request, **kwargs):
        """Создание народной новости пользователем"""

        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        if not request.user.profile.is_banned:
            form = FlashForm(request.POST)
            gallery_form = gallery_formset(request.POST, request.FILES, instance=Flash())
            if form.is_valid() and gallery_form.is_valid():
                instance = form.save(commit=False)
                instance.author = request.user
                instance.type = Flash.SITE
                instance.created = datetime.datetime.now()
                instance.save()

                self._notify(instance)

                gallery_form = gallery_formset(request.POST, request.FILES, instance=instance)
                # Заново вызываем валидацию, чтобы получить заполненный `gallery_form.is_valid`
                gallery_form.is_valid()
                gallery_form.save()

        return redirect('news:flash:index')

    def get(self, request, **kwargs):
        """Отображение страницы"""

        self._parse_params()

        context = self._get_context()

        if request.is_ajax():
            return JsonResponse(
                {'data': render_to_string('news-less/flash/snippets/entries.html', context, request=request)}
            )

        return render(request, 'news-less/flash/index.html', context)

    def _parse_params(self):
        """Разобрать параметры запроса"""

        self._page_number = int_or_none(self.request.GET.get('page')) or 1

        self._show_hidden = is_flash_moderator(self.request.user)

    def _get_context(self):
        """Получить контекст ответа"""

        form = FlashForm()
        gallery_form = gallery_formset(instance=Flash())

        main_list = self._get_main_list()
        if not self._show_hidden:
            main_list = main_list.filter(visible=True)

        sidebar_list = self._get_sidebar_list()
        sidebar_list = sidebar_list.filter(visible=True)

        main_list, page = self._paginate(main_list)

        context = {
            'form': form,
            'gallery_form': gallery_form,
            'show_hidden': self._show_hidden,
            'main_list': main_list,
            'sidebar_list': sidebar_list[:self.sidebar_limit],
            'page': page,
            'title': self.title,
            'sidebar_title': self.sidebar_title,
            'sidebar_url': self.sidebar_url,
        }

        return context

    def _get_main_list(self):
        """Получить основный список новостей"""

        queryset = Flash.objects.exclude(type=Flash.VK_DTP).order_by('-created').select_related('author')

        return queryset

    def _get_sidebar_list(self):
        """Получить дополнительный список новостей. Отображается в правой колонке"""

        queryset = Flash.objects.filter(type=Flash.VK_DTP).order_by('-created').select_related('author')

        return queryset

    def _paginate(self, object_list):
        """
        Пагинация

        :return: список объектов на странице и сама страница
        :rtype: list, Page
        """

        paginator = Paginator(object_list, self.main_limit)

        try:
            page = paginator.page(self._page_number)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)

        return page.object_list, page

    def _notify(self, instance):
        """Уведомить модераторов"""

        tpl_notify(
            u'Добавлена народная новость', 'news/notif/flash/add.html', {'instance': instance}, self.request,
            emails=get_flash_moderators().values_list('email', flat=True)
        )


class IndexDtpView(IndexView):
    """Главная новостей о дтп"""

    title = u'Лента ДТП'
    sidebar_title = u'Народные новости'
    sidebar_url = reverse_lazy('news:flash:index')

    def _get_context(self):
        context = super(IndexDtpView, self)._get_context()

        # Флаг для определения, что открыта страница о ДТП
        context['dtp_page'] = True

        return context

    def _get_main_list(self):
        # меняем основной список на список из правой колонки
        return super(IndexDtpView, self)._get_sidebar_list()

    def _get_sidebar_list(self):
        # меняем список правой колонки на основной список
        return super(IndexDtpView, self)._get_main_list()


def data(request):
    """Хак для передачи данных галерей на страницу списка новостей

    Нужен, потому что записи подгружаются ajax'ом, а браузеры в ajax ответе режут теги <script>,
    в которых и содержатся данные галерей."""

    if 'ids' in request.GET:
        ids = []
        for item in request.GET.get('ids', '').split(','):
            try:
                ids.append(int(item))
            except (TypeError, ValueError):
                continue

        objects = Flash.objects.filter(pk__in=ids)

    else:
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1

        paginate = Paginator(Flash.objects.filter(visible=True).order_by('-created'), 20)

        try:
            objects = paginate.page(page)
        except (EmptyPage, InvalidPage):
            objects = paginate.page(paginate.num_pages)

        objects = objects.object_list

    data = {}
    for obj in objects:
        if obj.is_sms:
            # Для SMS нет галерей
            continue

        if obj.is_site:
            obj_data = {}
            try:
                gallery = list(obj.gallery.main_gallery())
            except TypeError:
                continue
            if not len(gallery):
                continue

            for idx, item in enumerate(gallery):
                try:
                    thumbnail = DjangoThumbnail(item.image, (10000, 35))
                except ThumbnailException:
                    continue

                obj_data[idx] = {
                    'full': {
                        'src': item.image.url,
                        'width': item.image.width,
                        'height': item.image.height,
                    },
                    'alt': item.alt,
                    'src': thumbnail.absolute_url,
                    'width': thumbnail.width(),
                    'height': thumbnail.height()
                }

            data[obj.pk] = obj_data
            continue

        if obj.is_tweet:
            images = twitter_images(obj.content)
            if not len(images):
                continue

            obj_data = {}
            for idx, image in enumerate(images):
                obj_data[idx] = {
                    'full': {
                        'src': image['image'],
                        'width': 'auto',
                        'height': 'auto'
                    },
                    'alt': '',
                    'src': image['image'],
                    'width': 'auto',
                    'height': 'auto',
                }

            data[obj.pk] = obj_data
            continue

    return JsonResponse(data)


def read(request, flash_id):
    """Просмотр народной новости"""

    entry = get_object_or_404(Flash, pk=flash_id, visible=True)
    moderator = is_flash_moderator(request.user)

    context = {
        'entry': entry,
        'moderator': moderator,
    }

    if entry.video_thumbnail:
        context['video_url'] = FlashVideoPreviewGrabber(entry).get_embed_url()

    return render(request, 'news-less/flash/read.html', context)


def toggle(request, flash_id):
    """Удаление народной новости"""

    entry = get_object_or_404(Flash, pk=flash_id)
    moderator = is_flash_moderator(request.user)
    if not moderator:
        return HttpResponseForbidden(u'Нет прав на удаление народных новостей')

    entry.visible = not entry.visible
    entry.save()

    context = {
        'entry': entry,
        'moderator': moderator,
    }

    if request.is_ajax():
        if entry.is_sms:
            html = render_to_string('news-less/flash/snippets/sms.html', context)
        elif entry.is_site:
            html = render_to_string('news-less/flash/snippets/site.html', context)
        elif entry.is_tweet:
            html = render_to_string('news-less/flash/snippets/tweet.html', context)
        else:
            html = ''
        return JsonResponse({'success': True, 'html': html})

    return redirect(reverse('news:flash:index'))


index = IndexView.as_view()
index_dtp = IndexDtpView.as_view()
