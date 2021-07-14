# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.db.models import Max
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.core.cache import cache
from django.core.validators import FileExtensionValidator

from irk.gallery import managers
from irk.gallery.cache import invalidate
from irk.gallery.settings import ALLOWED_EXTENSIONS
from irk.gallery.signals import clean_thumbnails_post_save, clean_thumbnails_pre_save

from irk.utils.fields.file import ImageRemovableField


class Gallery(models.Model):
    """Галерея"""

    name = models.CharField(u'Название', max_length=255, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, editable=False)
    object_id = models.PositiveIntegerField(null=True, editable=False)
    parent_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, editable=False, null=True)
    pictures = models.ManyToManyField(to='Picture', through='GalleryPicture')
    stamp = models.DateTimeField(null=True, default=datetime.datetime.now)

    objects = managers.GalleryManager()

    class Meta:
        verbose_name = u'галерею'
        verbose_name_plural = u'галереи'

    @property
    def main(self):
        """Главное изображение галереи"""

        key = 'gallery:main_picture:%s' % self.pk
        picture_pk = cache.get(key)
        if not picture_pk:
            try:
                picture = self.gallerypicture_set.get(main=True).picture
            except GalleryPicture.DoesNotExist:
                picture = self.gallerypicture_set.all().order_by('position')[0].picture
            except GalleryPicture.MultipleObjectsReturned:
                self.gallerypicture_set.all().update(main=False)
                gallery_picture = self.gallerypicture_set.all().order_by('position').select_related('picture')[0]
                GalleryPicture.objects.filter(pk=gallery_picture.pk).update(main=True)
                picture = gallery_picture.picture

            cache.set(key, picture.pk, 60 * 60 * 24)

            return picture

        try:
            return self.gallerypicture_set.get(pk=picture_pk)
        except GalleryPicture.DoesNotExist:
            pass

        return None


def upload_to(object, filename):
    folder = Picture.objects.count() / 500 + 1
    return 'img/site/gallery/%s/%s' % (folder, filename)

post_save.connect(invalidate, sender=Gallery)


class Picture(models.Model):
    """Изображение"""

    image = ImageRemovableField(upload_to=upload_to, verbose_name=u'Изображение',
                             validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)])
    title = models.CharField(max_length=255, verbose_name=u'Описание')
    date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, editable=False, null=True)
    watermark = models.BooleanField(u'Вотермарк', default=False)

    class Meta:
        verbose_name = u'изображение'
        verbose_name_plural = u'изображение'

    def __unicode__(self):
        return self.title

    def get_alt(self):
        return self.title
    alt = property(get_alt)

pre_save.connect(clean_thumbnails_pre_save, sender=Picture)
post_save.connect(clean_thumbnails_post_save, sender=Picture)
post_save.connect(invalidate, sender=Picture)


class GalleryPicture(models.Model):
    """Привязка изображений к галереям"""

    picture = models.ForeignKey(Picture, verbose_name=u'Изображение')
    gallery = models.ForeignKey(Gallery, verbose_name=u'Галерея')
    position = models.PositiveSmallIntegerField(verbose_name=u'Позиция', blank=True)
    main = models.BooleanField(verbose_name=u'Основная', default=False)
    best = models.BooleanField(verbose_name=u'Лучшая', default=False)

    def save(self, *args, **kwargs):
        if not self.position:
            try:
                self.position = GalleryPicture.objects.filter(gallery__id=self.gallery.pk).\
                    aggregate(max=Max('position'))['max'] + 1
            except TypeError:
                self.position = 1
                self.main = True
        super(GalleryPicture, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'рис'
        verbose_name_plural = u'рис.'
        ordering = ['position']
        unique_together = ('picture', 'gallery')

    def __unicode__(self):
        return u'рис.%s' % self.position

post_save.connect(invalidate, sender=GalleryPicture)
