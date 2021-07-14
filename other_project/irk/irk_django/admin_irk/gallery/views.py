# -*- coding: utf-8 -*-

import datetime
import logging
from importlib import import_module

from PIL import Image
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from sorl.thumbnail.main import DjangoThumbnail

from irk.gallery.forms.admin import PicForm
from irk.gallery.models import Picture, GalleryPicture, Gallery
from irk.utils.helpers import get_object_or_none, int_or_none
from irk.utils.http import JsonResponse

logger = logging.getLogger(__name__)


@csrf_exempt
def admin_multiupload_handler(request):
    """Обработчик запросов на сохранение файлов от multiuploader из админки."""

    content_type_id = request.POST.get('content_type_id')
    object_id = request.POST.get('object_id')

    if content_type_id and object_id:
        # Объект редактируется
        gallery, _ = Gallery.objects.get_or_create(content_type_id=content_type_id, object_id=object_id)
    elif content_type_id and not object_id:
        # Объект создается
        gallery, _ = Gallery.objects.get_or_create(content_type_id=content_type_id, user=request.user, object_id=None)
    else:
        raise Http404

    form = PicForm(
        data=request.POST,
        files={'image': request.FILES.get('Filedata')}
    )

    if form.is_valid():
        pic = form.save(commit=False)
        pic.save()
        gpic = GalleryPicture.objects.create(picture=pic, gallery=gallery)

        thumb = DjangoThumbnail(pic.image, (100, 10000))
        origial_image = Image.open(pic.image.path)

        context = {
            'picture': pic.pk,
            'image': {
                'path': unicode(thumb),
                'height': thumb.height(),
                'width': thumb.width(),
            },
            'origial_height': origial_image.size[1],
            'origial_width': origial_image.size[0],
            'gallerypicture': gpic.pk,
            'gallery': gallery.pk,
        }

    else:
        context = {'error': form.errors}

    return JsonResponse(context, content_type='text/html')


#@login_required  # TODO: выяснить, почему не работает
@csrf_exempt
def multiupload_handler(request):

    gpic_id = int_or_none(request.POST.get('id'))
    gpic = get_object_or_404(GalleryPicture, pk=gpic_id) if gpic_id else None

    gallery_id = request.POST.get('gallery_id')
    gallery = get_object_or_none(Gallery, pk=gallery_id) if gallery_id else None

    if not gallery:
        content_type_id = request.POST.get('content_type_id')
        if not content_type_id:
            raise Http404('Not found content type id!')

        object_id = request.POST.get('object_id')

        if object_id:
            content_type = ContentType.objects.get(pk=content_type_id)
            obj = content_type.get_object_for_this_type(pk=object_id)
            gallery = obj.main_gallery()
        else:
            # Объект создается, поэтому привязываем галерею к content_type и идентификатору пользователя.
            if request.user.is_authenticated:
                user_id = request.user.pk
            else:
                # TODO: определить актуальность случая, когда пользователь не авторизован
                session_key = request.POST.get('session_key')
                engine = import_module(settings.SESSION_ENGINE)
                session = engine.SessionStore(session_key)
                if SESSION_KEY in session:
                    user_id = session[SESSION_KEY]
                else:
                    raise Http404

            gallery = Gallery.objects.filter(content_type_id=content_type_id, object_id=None, user_id=user_id).last()
            if not gallery:
                gallery = Gallery.objects.create(content_type_id=content_type_id, user_id=user_id)
            gallery.stamp = datetime.datetime.now()
            gallery.save()

    form = PicForm(
        data=request.POST,
        files={'image': request.FILES.get('Filedata')}
    )

    if form.is_valid():
        pic = form.save()
        if not gpic:
            gpic = GalleryPicture.objects.create(picture=pic, gallery=gallery)
        else:
            gpic.picture.delete()
            gpic.picture = pic
            gpic.save()
        thumb = DjangoThumbnail(pic.image, (100, 10000))
        origial_image = Image.open(pic.image.path)

        context = {
            'picture': pic.pk,
            'image': {
                'path': unicode(thumb),
                'height': thumb.height(),
                'width': thumb.width(),
            },
            'origial_height': origial_image.size[1],
            'origial_width': origial_image.size[0],
            'gallerypicture': gpic.pk,
            'gallery': gallery.pk,
        }

    else:
        context = {'error': form.errors}

    return JsonResponse(context, content_type='text/html')


@login_required
def delete_image(request):
    image_id = request.POST.get('id')
    picture = get_object_or_404(Picture, id=image_id)
    gallery_picture = get_object_or_404(GalleryPicture, picture=picture)

    is_main = gallery_picture.main
    is_best = gallery_picture.best
    gallery = gallery_picture.gallery

    gallery_picture.delete()
    picture.delete()

    # Если удаляемая фотка главная, то делаем голавной первую из оставшихся
    if is_main:
        try:
            first_picture = GalleryPicture.objects.filter(gallery=gallery)[0]
            first_picture.main = True
            first_picture.save()
            return JsonResponse({'main': 0})
        except IndexError:
            pass

    # Если удаляемая фотка лучшая, то делаем голавной первую из оставшихся
    if is_best:
        try:
            first_picture = GalleryPicture.objects.filter(gallery=gallery)[0]
            first_picture.best = True
            first_picture.save()
            return JsonResponse({'main': 0})
        except IndexError:
            pass

    return JsonResponse({})


@login_required
def main_image(request):
    """Установка главной картинки"""
    image_id = request.GET.get('id')
    picture = get_object_or_404(Picture, id=image_id, )
    gallery_picture = get_object_or_404(GalleryPicture, picture=picture)

    gallery_picture.main = True
    gallery_picture.save()
    GalleryPicture.objects.filter(gallery=gallery_picture.gallery) \
        .exclude(pk=gallery_picture.pk).update(main=False)

    return HttpResponse('')


@login_required
def best_image(request):
    """Установка/удалние лучшей картинки"""
    image_id = request.GET.get('id')
    remove = request.GET.get('remove')
    picture = get_object_or_404(Picture, id=image_id, )
    gallery_picture = get_object_or_404(GalleryPicture, picture=picture)

    if remove:
        gallery_picture.best = False
    else:
        gallery_picture.best = True
    gallery_picture.save()
    GalleryPicture.objects.filter(gallery=gallery_picture.gallery) \
        .exclude(pk=gallery_picture.pk).update(best=False)

    return HttpResponse('')


@login_required
def set_watermark(request):
    """Установить/снять ватермарк для картинки"""
    image_id = request.POST.get('id')
    picture = get_object_or_404(Picture, id=image_id)
    picture.watermark = not picture.watermark
    picture.save()

    # TODO: возвращать осмысленный ответ
    return JsonResponse({})


@login_required
def set_watermark_all(request):
    """Установить/снять ватермарк для картинок в галереи"""
    gallery_id = request.POST.get('id')
    check = request.POST.get('check') == 'true'
    for gallery_picture in GalleryPicture.objects.filter(gallery_id=gallery_id):
        picture = gallery_picture.picture
        picture.watermark = check
        picture.save()

    # TODO: возвращать осмысленный ответ
    return JsonResponse({})
