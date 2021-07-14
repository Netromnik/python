# -*- coding: utf-8 -*-

from django.forms import ValidationError
from PIL import Image as ImageLib

from irk.utils.fields.file import RemovableImageFormField, RemovableImageField


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class ImageFormField(RemovableImageFormField):
    def __init__(self, min_size=(0, 0), max_size=(0, 0), allow=(), *args, **kwargs):
        super(ImageFormField, self).__init__(*args, **kwargs)
        self.min_size, self.max_size = min_size, max_size
        self.allow = allow

    def clean(self, data, initial=None):
        f = super(ImageFormField, self).clean(data)
        if f and data[0]:
            try:
                if hasattr(data[0], 'temporary_file_path'):
                    output = data[0].temporary_file_path()
                else:
                    if hasattr(data[0], 'read'):
                        output = StringIO(data[0].read())
                    else:
                        output = StringIO(data[0]['content'])

                try:
                    trial_image = ImageLib.open(output)
                    trial_image.load()
                except IOError:
                    raise ValidationError(u"Ошибочный файл")

                # hack: иногда из твиттера загружаются файлы .jpg_large - поправим это
                if f[0].name.endswith('.jpg_large'):
                    f[0].name = f[0].name.replace('.jpg_large', '.jpg')

                ext = f[0].name.split(".").pop()
                if self.allow and ext not in self.allow:
                    raise ValidationError(u'Недопустимый тип файла %s' % ext)

                width, height = trial_image.size
                if width > self.max_size[0] or height > self.max_size[1]:
                    raise ValidationError(u"Разрешение файла превышает %dx%d" % self.max_size)

                if width < self.min_size[0] or height < self.min_size[1]:
                    raise ValidationError(u"Разрешение файла меньше %dx%d" % self.min_size)
            except ImportError:
                raise ValidationError(u"Ошибочка вышла.")
        return f


# DEPRECATED, используйте irk.utils.ImageRemoveField
class Image(RemovableImageField):
    min_size = None
    max_size = None

    def __init__(self, min_size=(0, 0), max_size=(8192, 4320), allow=(), *args, **kwargs):
        self.min_size, self.max_size = min_size, max_size
        self.allow = allow
        super(Image, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': ImageFormField,
            'min_size': self.min_size,
            'max_size': self.max_size,
            'allow': self.allow,
        }
        defaults.update(kwargs)

        return super(Image, self).formfield(**defaults)

# South introspection rules for Image field
rules = [
    (
        (Image,), [], {
            #'verbose_name': ('verbose_name', {'default': None}),
            #'name': ('name', {'default': None}),
            #'upload_to': ('upload_to', {'default': models.fields.NOT_PROVIDED}),
            #'storage': ('storage', {'storage': None}),
        },
    ),
]
