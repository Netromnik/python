# -*- coding: utf-8 -*-

from django.db import models
from django.core.cache import cache

from irk.gallery.helpers import get_parent_content_type


CACHE_EMPTY_VALUE = object()


class GalleryManager(models.Manager):

    content_type_updated = False
    main_image_cache_lifetime = 60 * 60 * 24
    best_image_cache_lifetime = 60 * 60 * 24

    def __init__(self):
        super(GalleryManager, self).__init__()

        self._main_image = CACHE_EMPTY_VALUE
        self._best_image = CACHE_EMPTY_VALUE

    def get_content_type(self,):
        if not self.content_type_updated:
            self.content_type = get_parent_content_type(self.instance)
            self.core_filters['content_type__pk'] = self.content_type.pk
            self.content_type_updated = True
        return self.content_type

    def main_image(self):
        """Главное изображение галереи
        Если главного изображения нет, берется первое из всех изображений"""

        if self._main_image is not CACHE_EMPTY_VALUE:
            return self._main_image

        content_type = self.get_content_type()

        # self.instance - объект привязанной модели, например новости
        key = ':'.join(['gallery', 'main', content_type.app_label, content_type.model, str(self.instance.pk)])
        image_id = cache.get(key, default=CACHE_EMPTY_VALUE)

        if image_id == CACHE_EMPTY_VALUE:
            # В кэше нет идентификатора главного изображения, делаем выборку из базы
            from irk.gallery.models import GalleryPicture
            gallery_qs = list(self.get_queryset().all().values_list('id', flat=True))
            try:
                image_id = GalleryPicture.objects.filter(main=True, gallery=gallery_qs[0]).values_list('picture_id', flat=True)[0]
            except IndexError:
                # Главного изображения нет, берем первое и назначаем его главным
                try:
                    gallery_picture = GalleryPicture.objects.filter(gallery=gallery_qs[0]).order_by('position')[0]
                    gallery_picture.main = True
                    gallery_picture.save()
                    image_id = gallery_picture.picture_id
                except IndexError:
                    image_id = None

            cache.set(key, image_id, self.main_image_cache_lifetime)

        if image_id is None:
            self._main_image = None
            return

        from irk.gallery.models import Picture

        try:
            self._main_image = Picture.objects.get(pk=image_id)
        except Picture.DoesNotExist:
            self._main_image = None

        return self._main_image

    def best_image(self):
        """Лучшее изображение галереи
        Если лучшего изображения нет, берется первое из всех изображений"""

        if self._best_image is not CACHE_EMPTY_VALUE:
            return self._best_image

        content_type = self.get_content_type()

        # self.instance - объект привязанной модели, например новости
        key = ':'.join(['gallery', 'best', content_type.app_label, content_type.model, str(self.instance.pk)])
        image_id = cache.get(key, default=CACHE_EMPTY_VALUE)

        if image_id == CACHE_EMPTY_VALUE:
            # В кэше нет идентификатора главного изображения, делаем выборку из базы
            from irk.gallery.models import GalleryPicture
            gallery_qs = list(self.get_queryset().all().values_list('id', flat=True))
            try:
                image_id = GalleryPicture.objects.filter(best=True, gallery=gallery_qs[0]) \
                    .values_list('picture_id', flat=True)[0]
            except IndexError:
                image_id = None

            cache.set(key, image_id, self.best_image_cache_lifetime)

        if image_id is None:
            self._best_image = None
            return

        from irk.gallery.models import Picture

        try:
            self._best_image = Picture.objects.get(pk=image_id)
        except Picture.DoesNotExist:
            self._best_image = None

        return self._best_image

    def has_best_image(self):
        gallery = self.main()
        if gallery:
            return gallery.pictures.filter(gallerypicture__best=True).exists()
        return False

    # TODO: метод называется "главная галерея", а возвращает объекты pictures
    def main_gallery(self):
        ct = self.get_content_type()
        try:
            return self.model.objects.filter(
                content_type=ct,
                object_id=self.instance.pk
            )[0].pictures.all().order_by('-gallerypicture__main', 'gallerypicture__position')
        except IndexError:
            # TODO: Было бы более корректно возвращать пустой список
            return None

    def main_gallery_pictures(self):
        queryset = self.main_gallery()
        if queryset is None:
            return
        return queryset.exclude(gallerypicture__main=True)

    def main(self):
        """
        Вернуть главную галерею для связанного объекта.
        Можно использовать только для RelatedManager.

        :rtype: gallery.models.Gallery
        :raises: AttributeError - если вызвать для обычного Manager
        """

        if self.instance:
            return self.model.objects.filter(content_type=self.get_content_type(), object_id=self.instance.pk).first()
