# -*- coding: UTF-8 -*-
"""
    Все формы которые используются в аднмине галерей.
"""
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

import fields
from irk.gallery import models as gallery_models
from irk.gallery.helpers import get_parent_content_type
from irk.utils.helpers import get_object_or_none


class GalleryInlineFormset(forms.models.BaseInlineFormSet):
    parent_instance = None
    user = None

    def __init__(self, *args, **kwargs):
        """Замена создаваемого объекта (параметр instance) на галерею для него"""

        # создаваемый/редактируемый объект
        instance = kwargs.get('instance')
        user = kwargs.pop('user', None) or self.user

        # Сохраняем оригинальный объект, для которого добавляется галерея.
        # self.instance будет указывать на галерею для этого объекта
        self.original_instance = instance
        instance = self._get_instance_if_proxy(instance)
        parent_ct = get_parent_content_type(instance)

        gallery = None

        if instance.pk:
            # Объект редактируется, ищем галерею в БД
            gallery = gallery_models.Gallery.objects.filter(content_type=parent_ct, object_id=instance.pk).first()

        if not gallery:
            if user and user.is_authenticated:
                # пытаемся найти галерею для подобных объектов (по content_type)
                # созданную данным пользователем ранее
                gallery = (
                    gallery_models.Gallery.objects.filter(user=user, content_type=parent_ct, object_id=None).first()
                )

        # Галерея все еще не найдена, создаем новую
        if not gallery:
            gallery = gallery_models.Gallery(content_type=parent_ct, object_id=instance.pk)

        kwargs['instance'] = gallery
        super(GalleryInlineFormset, self).__init__(*args, **kwargs)

    def _get_instance_if_proxy(self, instance):
        """
        Если instance проксирующая модель, то ищем оригинал

        :param instance: создаваемый/редактируемый объект
        :rtype: django.db.models.Model
        """
        opts = instance._meta
        if opts.proxy:
            try:
                instance = opts.proxy_for_model.objects.get(id=instance.pk)
            except ObjectDoesNotExist:
                pass

        return instance

    def get_instance_from_obj(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        if obj.pk:
            obj = gallery_models.Gallery(content_type=ct, object_id=obj.pk)
            obj.save()
        else:
            obj = gallery_models.Gallery(content_type=ct, object_id=obj.pk)

        return obj

    def save(self, *args, **kwargs):
        if not self.original_instance.pk:
            self.original_instance.save()

        self.instance.object_id = self.original_instance.pk
        self.instance.save()

        return super(GalleryInlineFormset, self).save(*args, **kwargs)


data = {'help_text': '', 'max_length': 100, 'label': u'\u041b\u043e\u0433\u043e\u0442\u0438\u043f', 'required': False}


class PictureForm(forms.ModelForm):
    picture = fields.Picture(label=u'Изображение', required=True)

    def __init__(self, *args, **kwargs):
        super(PictureForm, self).__init__(*args, **kwargs)

    class Meta:
        models = gallery_models.GalleryPicture


class PicForm(forms.ModelForm):
    title = forms.CharField(required=False)

    class Meta:
        model = gallery_models.Picture
        fields = '__all__'


class InlinePictureForm(PictureForm):
    class Meta:
        model = gallery_models.GalleryPicture
        exclude = ('gallery', 'position', 'main', 'best')


class InlineGalleryFormset(forms.models.BaseInlineFormSet):
    pass
