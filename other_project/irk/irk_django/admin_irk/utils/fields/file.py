# -*- coding: utf-8 -*-

import os
import re
import shutil
import zipfile
# from hexagonit import swfheader

from django import forms
from django.conf import settings
from django.contrib.admin import widgets
from django.core.files.images import ImageFile
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe


class AdminImageReadonlyWidget(forms.Widget):
    """Виджет для отображения загруженной картинки без возможности редактирования"""

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            return mark_safe(u'<img src="{0.url}">'.format(value))
        else:
            return u'Нет изображения'


class MediaFieldFile(ImageFile, FieldFile):
    def __init__(self, *args, **kwargs):
        super(MediaFieldFile, self).__init__(*args, **kwargs)

    def _get_file_type(self):
        try:
            return self.file.name.split(".").pop()
        except Exception:
            pass

    file_type = property(_get_file_type)

    def _get_image_dimensions(self):
        try:
            dims = super(MediaFieldFile, self)._get_image_dimensions()
            if dims:
                return dims
        except Exception:
            pass

        # Пытаемся обработать как SVF
        # !TODO Хз кому флеш нужен
        # try:
        #     self.file.open()
        #     metadata = swfheader.parse(self.file)
        #     self.file.close()
        #     return metadata['width'], metadata['height']
        # except Exception:
        #     pass

        return None, None


class FileRemovableField(models.FileField):
    """
    Field with deleting the file by default
    """

    def delete_file(self, field_obj):
        field_obj.delete(save=False)

    def save_form_data(self, instance, data):
        field_obj = getattr(instance, self.name)

        if data is not None:
            # Delete file
            if not data:
                data = ''
                self.delete_file(field_obj)
            # Replace file
            elif field_obj and field_obj != data:
                self.delete_file(field_obj)
            setattr(instance, self.name, data)


class AdminImagePreviewWidget(AdminFileWidget):
    """
    Виджет для админской формы с превьюшкой изображения
    """
    template_name = 'admin/widgets/clearable_image_file_input.html'
    initial_text = u'Оригинал'


class ImageRemovableField(FileRemovableField, models.ImageField):
    pass


class ArchiveFieldFile(MediaFieldFile):
    """
    Архивный файл с медиа данными

    На данный момент хранит баннер в формате html5
    """

    def delete(self, save=True):
        """Удаление файла архива и распакованных данных"""

        self.clean_extract()
        super(ArchiveFieldFile, self).delete(save)

    def extract(self):
        """Распаковать данные"""

        path = self.extract_path
        if os.path.isfile(self.path):
            with zipfile.ZipFile(self.path) as zf:
                zf.extractall(path)

    def fix_external_links(self):
        """
        Проверка наличия ссылок на внешние ресурсы в файлах js, css, html
        Ссылки внутри комментариев не учитываются
        """

        from irk.utils.files.helpers import static_link

        # Путь до директории скриптов использующихся в html5 банерах
        banner_libs_path = 'js/lib/banner/'
        banner_libs_full_path = os.path.join(settings.STATIC_ROOT, banner_libs_path)
        local_libs = tuple(os.listdir(banner_libs_full_path))

        bad_replaces = []
        for root, dirs, files in os.walk(self.extract_path):
            for file_ in files:
                if file_.endswith(('.js', '.css', '.html')):
                    replaces = []
                    full_path = os.path.join(self.extract_path, root, file_)
                    with open(full_path, 'r+b') as fp:
                        original_data = fp.read()
                        fp.seek(0)

                        data = original_data
                        if full_path.endswith('.html'):
                            pattern = re.compile("(?<=<!--)(.*?)(?=-->)", re.MULTILINE | re.DOTALL)
                            data = pattern.sub('', data)
                            # Встроенный js
                            pattern = re.compile("(?<=\/\*)(.*?)(?=\*\/)", re.MULTILINE | re.DOTALL)
                            data = pattern.sub('', data)
                        elif full_path.endswith('.js') or full_path.endswith('.css'):
                            pattern = re.compile("(?<=\/\*)(.*?)(?=\*\/)", re.MULTILINE | re.DOTALL)
                            data = pattern.sub('', data)

                        if 'http://' in data or 'https://' in data:
                            pattern = re.compile("(https?\://[^\"|\'|\s]*)", re.MULTILINE | re.DOTALL)
                            links = pattern.findall(data)
                            for link in links:
                                if not link.endswith(local_libs):
                                    bad_replaces.append([file_, link])
                                else:
                                    replaces.append(link)

                        # Замена внешних ссылок на локальные
                        if replaces:
                            data = original_data
                            for link in replaces:
                                local_file = os.path.join(banner_libs_path, link.split('/')[-1])
                                local_link = str(static_link(local_file))
                                data = data.replace(link, local_link)
                            fp.write(data)

        if bad_replaces:
            return bad_replaces
        return False

    def clean_extract(self):
        """Очистить распакованные данные"""

        if self.is_extract():
            shutil.rmtree(self.extract_path)

    def is_extract(self):
        """Распакован ли архив?"""

        return os.path.exists(self.extract_path)

    @cached_property
    def extract_path(self):
        """Путь для распакованных данных"""

        return os.path.splitext(self.path)[0]


class FileArchiveField(FileRemovableField):
    attr_class = ArchiveFieldFile
