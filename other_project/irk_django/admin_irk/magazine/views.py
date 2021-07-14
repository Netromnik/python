# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import datetime

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from irk.magazine.models import Magazine, MagazineSubscriber
from irk.news.models import BaseMaterial, Article, Photo
from irk.news.permissions import is_moderator as is_news_moderator
from irk.news.views.articles import ArticleReadView
from irk.news.views.photo import PhotoReadView
from irk.testing.models import Test
from irk.testing.views import TestReadView
from irk.utils.http import ajax_request
from irk.utils.notifications import tpl_notify


def index(request):
    """Index page for magazines"""

    magazines = Magazine.objects.all()
    if not is_news_moderator(request.user):
        magazines = magazines.visible()

    magazine = magazines.order_by('-pk').first()

    is_moderator = is_news_moderator(request.user)
    if not is_moderator and not magazine.visible:
        raise Http404()

    materials = BaseMaterial.magazine_objects.filter(magazine=magazine).order_by('magazine_position')
    if not is_moderator:
        materials = materials.filter(is_hidden=False)

    context = {
        'magazine': magazine,
        'materials': [m.cast() for m in materials],
        'next_magazine': Magazine.objects.visible().filter(pk__lt=magazine.pk).order_by('-pk').first(),
    }
    return render(request, 'magazine/index.html', context)


def read(request, slug):
    """Read page for magazine by slug"""

    magazine = get_object_or_404(Magazine, slug=slug)

    is_moderator = is_news_moderator(request.user)
    if not is_moderator and not magazine.visible:
        raise Http404()

    materials = BaseMaterial.magazine_objects.filter(magazine=magazine).order_by('magazine_position')
    if not is_moderator:
        materials = materials.filter(is_hidden=False)

    context = {
        'magazine': magazine,
        'materials': [m.cast() for m in materials],
        'next_magazine': Magazine.objects.visible().filter(pk__lt=magazine.pk).order_by('-pk').first(),
    }

    if request.is_ajax():
        template_name = 'magazine/list_item.html'
    else:
        template_name = 'magazine/read.html'

    return render(request, template_name, context)


def material_router(request, magazine_slug, material_id):
    """Роутер материалов журнала. Вызывает нужную вьюшку по типу материала"""

    magazine = get_object_or_404(Magazine, slug=magazine_slug)

    is_moderator = is_news_moderator(request.user)
    if not is_moderator and not magazine.visible:
        raise Http404()

    materials = BaseMaterial.magazine_objects.filter(magazine=magazine, pk=material_id)
    if not is_moderator:
        materials = materials.filter(is_hidden=False)
    material = materials.select_subclasses().first()

    if material:
        kwargs = {
            'year': material.stamp.year,
            'month': material.stamp.month,
            'day': material.stamp.day,
            'slug': material.slug,
        }
        if isinstance(material, Article):
            return ArticleReadView.as_view()(request, **kwargs)
        elif isinstance(material, Photo):
            return PhotoReadView.as_view()(request, **kwargs)
        elif isinstance(material, Test):
            return TestReadView.as_view()(request, test_id=material.pk)
    raise Http404()


@ajax_request
def subscription_ajax(request):
    """
    Подписка на журнал через Ajax
    """

    email = request.json.get('email')
    if not email:
        return {'ok': False, 'msg': u'Не указан email'}

    try:
        validate_email(email)
    except ValidationError as e:
        return {'ok': False, 'msg': u'Неправильный email', 'errors': {'email': e.messages}}

    subscriber = MagazineSubscriber(email=email, hash_stamp=datetime.datetime.now(), is_active=False)
    subscriber.generate_hash()
    tpl_notify(
        u'Подтверждение на рассылку журнала Ирк.ру',
        'magazine/notif/subscription_confirm.html',
        {'subscriber': subscriber},
        request,
        [email]
    )

    return {'ok': True, 'msg': u'Подписка успешно оформлена'}


def subscription_confirm(request):
    """Подтверждение подписки"""

    hash_ = request.GET.get('hash')
    if not hash_:
        raise Http404()

    try:
        subscriber = MagazineSubscriber.objects.get(
            hash=hash_,
            hash_stamp__gte=datetime.datetime.now() - datetime.timedelta(2),
        )
    except MagazineSubscriber.DoesNotExist:
        try:
            MagazineSubscriber.objects.get(hash=hash_)
            return render(request, 'magazine/subscription/expired.html')
        except MagazineSubscriber.DoesNotExist:
            raise Http404()

    subscriber.is_active = True
    subscriber.save()

    return render(request, 'magazine/subscription/success.html', {'hash': subscriber.hash})


def subscription_unsubscribe(request):
    """Отмена подписки"""

    hash_ = request.GET.get('hash')

    subscriber = get_object_or_404(MagazineSubscriber, hash=hash_)
    email = subscriber.email
    subscriber.delete()
    magazine = Magazine.objects.filter(visible=True)

    return render(request, 'magazine/subscription/unsubscribe_ok.html', {'magazine': magazine, 'email': email})
