# -*- coding: utf-8 -*-

import httplib
import json
import random

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest, \
    HttpResponseNotFound, Http404, HttpResponseForbidden
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from irk.afisha.models import Review
from irk.map.models import Streets
from irk.news.models import Article, Photo
from irk.obed.models import Review as ObedReview
from irk.options.models import Site
from irk.phones.models import Sections, MetaSection
from irk.utils.decorators import nginx_cached
from irk.utils.http import JsonResponse
from irk.utils.settings import TEMPLATES_404
from irk.utils.tasks import send_discord_mistype

# TODO: переписать всё это нормально. Возможно сделать что-нибудь подобное `django.contrib.admin.ModelAdmin' для автокомплита к каждой модели
SEARCH_FIELDS = {}

for obj in settings.REVIEW_OBJECTS:
    SEARCH_FIELDS["%s_%s" % (settings.REVIEW_OBJECTS[obj][0],
                             settings.REVIEW_OBJECTS[obj][1])] = settings.REVIEW_OBJECTS[obj][2]

#Хак
SEARCH_FIELDS['afisha_guide'] = ("name",)
SEARCH_FIELDS['phones_firms'] = ("name",)
SEARCH_FIELDS['map_streets'] = ("name",)
SEARCH_FIELDS['map_route'] = ('title',)
SEARCH_FIELDS['auth_user'] = ('username',)
SEARCH_FIELDS['phones_sections'] = ('name', 'name_short',)
SEARCH_FIELDS['transport_stop'] = ('name',)
SEARCH_FIELDS['tagging_tag'] = ('name',)
SEARCH_FIELDS['tourism_tourbase'] = ('name',)
SEARCH_FIELDS['tourism_place'] = ('title',)
SEARCH_FIELDS['adv_place'] = ('name', 'id')
SEARCH_FIELDS['adv_client'] = ('name',)
SEARCH_FIELDS['obed_menutype'] = ('name',)


def get_objects(request, id):
    """Backend для автодополнения

    Параметры::
        id - pk ContentType модели
        q - текст для поиска
    """

    ct = ContentType.objects.get(pk=id)
    qs = request.GET.get('q')
    s = request.GET.copy()

    if 'q' in s:
        del s['q']
    if 'limit' in s:
        del s['limit']
    if 'timestamp' in s:
        del s['timestamp']

    if not ('%s_%s' % (ct.app_label, ct.model)) in SEARCH_FIELDS:
        return HttpResponseNotFound()

    q = Q(**{"%s__icontains" % SEARCH_FIELDS["%s_%s" % (ct.app_label, ct.model)][0]: qs})
    for field in SEARCH_FIELDS["%s_%s" % (ct.app_label, ct.model)][1:]:
        q = q | Q(**{"%s__icontains" % field: qs})
    objects = ct.model_class().objects.filter(q)

    if s:
        search = {}
        for k in s:
            if s[k]:
                search[str(k)] = s[k]
        objects = objects.filter(**dict(search))

    objects = sorted(list(objects), key=lambda x: len(unicode(x)))
    res = ["%s=%s" % (obj.pk, unicode(obj)) for obj in objects]

    return HttpResponse("\n".join(res))


def sections_suggest(request):
    """Автодополнение для рубрик телефонного справочника

    Реализован отдельно, потому что требует хитрый запрос,
    который в рамках штатного автодополнения не реализуем на данный момент"""

    query = request.GET.get('q')
    if not query:
        return HttpResponse('')

    metasection = request.GET.get('metasection')
    if metasection:
        sections = MetaSection.objects.get(alias=metasection).sections_set.\
            filter(level__in=(2, 3), name__icontains=query).values('pk', 'name')
    else:
        sections = Sections.objects.filter(level__in=(1, 2, 3), name__icontains=query).values('pk', 'name')

    return HttpResponse('\n'.join(['%s=%s' % (section['pk'], section['name']) for section in sections]))


def streets_suggest(request):
    """Автодополнение улиц для админци"""

    city_id = request.GET.get('city__id', 0)

    q = request.GET.get('q', '')
    try:
        limit = int(request.GET.get('limit'))
    except (TypeError, ValueError):
        limit = 10

    queryset = Streets.objects.filter(Q(name__icontains=q) | Q(name2__icontains=q)).filter(
        city=city_id).prefetch_related('city').distinct()[:limit]

    titles = []
    for entry in queryset:
        titles.append('%s=%s' % (entry.pk, entry.name))

    return HttpResponse('\n'.join(titles))


@csrf_exempt
def report(request):
    """Сообщение об ошибке (об опечатке)"""

    if not request.method == 'POST' or not request.is_ajax():
        return HttpResponseNotAllowed(['POST', ])

    url = request.POST.get('url')
    text = request.POST.get('text')
    description = request.POST.get('description')

    if url and text:
        context = {'url': url, 'text': text, 'description': description,
                   'browser': request.META.get('HTTP_USER_AGENT'), 'ip': request.META.get('REMOTE_ADDR')}
        if request.user.is_authenticated:
            context['user_authenticated'] = True
            context['user_id'] = request.user.id
            context['user_name'] = request.user.username
            context['user_link'] = 'https://www.irk.ru/adm/profiles/profileuser/{}/'.format(request.user.id)
        else:
            context['user_authenticated'] = False
            # TODO можно убрать через какое-то время когда спамеры успокоятся
            return HttpResponseForbidden()

        send_discord_mistype.delay(context)
    else:
        return HttpResponseBadRequest()

    if request.is_ajax():
        return JsonResponse({'status': 200})
    return HttpResponseRedirect('/')


def handler404(request, *args, **kwargs):
    """Кастомное представление для 404 ошибки

    Для AJAX страниц отдаем ответ без содержимого страницы"""

    if request.is_ajax():
        return HttpResponseNotFound()

    context = {
        'request_path': request.path,
    }

    filename = random.choice(TEMPLATES_404)

    return HttpResponseNotFound(render_to_string(filename, context, request=request))


def subdomain_handler404(request):
    """Кастомное представление для 404 ошибки
       для поддоменов на которые могут заходить только
       боты
    """
    return HttpResponseNotFound("")


@nginx_cached(60 * 60)
def navigation_bar(request):
    """JS файл с меню навигации для сторонних сайтов"""

    sites = Site.objects.filter(show_in_bar=True).order_by('position')
    data = []
    for item in sites:
        url = item.url if item.url else item.site
        if item.track_transition and item.slugs:
            url += '?utm_source=%s&utm_medium=nav' % item.slugs
        data.append({
            'name': item.name,
            'url': url,
            'title': item.title
        })
    response = render_to_string('utils/navigation.html', {'sites': json.dumps(data)}, request=request)

    return HttpResponse(response, content_type='text/javascript')


def ct_redirect(request, content_type_id, object_id):
    """Вьюшка для редиректа на страницу просмотра объекта"""

    try:
        content_type = ContentType.objects.get(pk=content_type_id)
        if not content_type.model_class():
            raise Http404("Content type %s object has no associated model" % content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ObjectDoesNotExist, ValueError):
        raise Http404("Content type %s object %s doesn't exist" % (content_type_id, object_id))
    return HttpResponseRedirect(obj.get_absolute_url())


def ct_redirect_adm(request, content_type_id, object_id):
    """Вьюшка для редиректа на страницу редактирования объекта"""

    try:
        content_type = ContentType.objects.get(pk=content_type_id)
        if not content_type.model_class():
            raise Http404("Content type %s object has no associated model" % content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ObjectDoesNotExist, ValueError):
        raise Http404("Content type %s object %s doesn't exist" % (content_type_id, object_id))
    return HttpResponseRedirect(obj.get_admin_url())


def handler410(request):
    """Заглушка для закрытых разделов"""

    club = Article.material_objects.filter(project__slug='club', is_hidden=False).order_by('stamp', 'pk').last()
    club.rubric_url = club.project.get_absolute_url()
    club.rubric_title = club.project.title
    favourite = Article.material_objects.filter(project__slug='favourite', is_hidden=False).order_by('stamp', 'pk').last()
    favourite.rubric_url = favourite.project.get_absolute_url()
    favourite.rubric_title = favourite.project.title
    review = Review.material_objects.filter(is_hidden=False).order_by('stamp', 'pk').last()
    review.rubric_url = reverse_lazy('afisha:review:index')
    review.rubric_title = u'Рецензии'
    photo = Photo.material_objects.filter(is_hidden=False).order_by('stamp', 'pk').last()
    photo.rubric_url = reverse_lazy('news:photo:index')
    photo.rubric_title = u'Фоторепортажи'
    obed_review = ObedReview.material_objects.filter(is_hidden=False).order_by('stamp', 'pk').last()
    obed_review.rubric_url = reverse_lazy('obed:index')
    obed_review.rubric_title = u'Обед'
    news = Article.material_objects.filter(is_hidden=False, category=None).order_by('stamp', 'pk').last()
    news.rubric_url = reverse_lazy('news:article:index')
    news.rubric_title = u'Статьи'

    context = {
        'article_list': [club, favourite, review, photo, obed_review, news]
    }

    response = render(request, '410/default.html', context)
    response.status_code = httplib.GONE
    response.reason_phrase = httplib.responses[httplib.GONE]

    return response

