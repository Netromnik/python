# -*- coding: utf-8 -*-

"""Class-based view для просмотра одной новости"""

__all__ = ('NewsReadBaseView',)

import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic.base import View

from irk.hitcounters.actions import hitcounter, hitcounter2
from irk.news.models import News, Article
from irk.news.permissions import is_site_news_moderator, can_see_hidden
from irk.news.views.base import SectionNewsBaseView
from irk.utils.cache import TagCache


class NewsReadBaseView(View):
    model = News
    template = None

    def get(self, request, **kwargs):
        """Обработка GET запроса"""

        obj = self.get_object(request, kwargs)

        hitcounter(request, obj)
        hitcounter2(request, obj)

        if isinstance(obj, HttpResponse):
            return obj

        context = {
            'object': obj,
        }
        context.update(self.extra_context(request, obj, kwargs))

        return render(request, self.get_template(request, obj, context), context)

    def get_object(self, request, extra_params=None):
        """Хелпер. возвращающий объект класса ``self.model``

        Параметры::
            request: объект класса `django.http.HttpRequest'
            extra_params: словарь параметров, переданных в view

        Если возвращается `django.http.HttpResponse' или его потомок, этот объект сразу отдается клиенту.
        Это позволит делать дополнительные проверки, можно ли редактировать пользователю этот объект.
        """

        try:
            self.date = datetime.date(int(extra_params['year']), int(extra_params['month']), int(extra_params['day']))
        except ValueError:
            raise Http404()

        kwargs = {
            'stamp': self.date,
        }

        if 'slug' in extra_params:
            kwargs['slug'] = extra_params['slug']
        elif 'id' in extra_params:
            kwargs['id'] = extra_params['slug']
        else:
            raise NotImplementedError(u'В параметрах не был передан slug или id объекта')

        show_hidden = self.show_hidden(request)

        ct = ContentType.objects.get_for_model(self.model)
        cache_key = '.'.join([ct.model, self.date.isoformat(), kwargs.get('slug') or kwargs.get('id'), str(request.csite.id)])
        with TagCache(cache_key, 86400, tags=('news', 'article', 'photo', 'video', 'review')) as cache:
            obj_id = cache.value
            if obj_id is cache.EMPTY:
                try:
                    obj = self.model.objects.distinct().filter(Q(source_site=request.csite.site) | Q(sites=request.csite.site), **kwargs)[0]
                    if not show_hidden and obj.is_hidden:
                        raise Http404(u'Объект скрыт')
                except IndexError:
                    raise Http404()

                cache.value = obj.id
            else:
                obj = self.model.objects.get(id=obj_id)
                if not show_hidden and obj.is_hidden:
                    raise Http404(u'Объект скрыт')

            return obj

    def extra_context(self, request, obj, extra_params=None):
        """Дополнительные данные для передачи в шаблон

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
            extra_params: словарь параметров, переданных в view

        Должен возвращаться словарь
        """

        context = {
            'date': self.date,
        }

        if issubclass(self.model, News) and obj.category_id:
            # Для новостей выводим категорию
            context['category'] = obj.category

        if issubclass(self.model, (News, Article)) and obj.subject_id:
            # для статей и новостей в сюжете Новый год 2019 выводится особое брендирование
            context['is_newyear2019'] = obj.subject.slug == 'newyear2019'

        context['social_statistic'] = getattr(obj, 'statistic_metrics', None)

        context['is_moderator'] = self.show_hidden(request)

        return context

    def get_template(self, request, obj, template_context):
        """Выбор шаблона для рендеринга

        Может возвращать список шаблонов, из которых будет выбран первый существующий

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
            template_context: словарь данных, который будет передан в шаблон
        """
        app_label = self.__module__.split('.')[1]

        return self.template or '%s/%s/read.html' % (app_label, self.model._meta.object_name.lower())

    def show_hidden(self, request):
        """Хелпер, определяющий, показывать ли скрытые новости

        Используется, например, если пользователь является модератором
        """

        return is_site_news_moderator(request) or can_see_hidden(request.user)


    def concretize(self, material):
        """Конкретизировать материал"""

        return material.content_object if not material.is_specific() else material


class SectionNewsReadBaseView(SectionNewsBaseView, NewsReadBaseView):
    """Базовый класс для новостей/статей разделов"""

    def get_object(self, request, extra_params=None):
        obj = super(SectionNewsReadBaseView, self).get_object(request, extra_params)
        if not obj.sites.filter(id=request.csite.id).exists():
            raise Http404()

        return obj
