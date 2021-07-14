# coding=utf-8
"""
Утилиты для распаковки Тильдовского архива и парсинга контента по пути.

Этот класс делают две вещи:

1. Распаковывает архив, но пропускает ненужные файлы. Какие файлы будут
распакованы в папку на сервере - решает метод extract_path.

2. При распаковке он вызывает функцию-обрабочик для каждого файла. Обрабочик реагирует
на файлы pagexxx.html и pagexxxbody.html и парсит из них стили, скрипты и контент.
Эти данные потом сохраняются в базу данных.

Ссылки хранятся в относительном виде: src="js/some.js", и при выводе теги правят
путь, дописывая к нему абсолютный адрес папки, куда распакован архив.

Подробнее: http://codepoetry.ru/post/tilda-django-integration/
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import re
import zipfile

from irk.utils.helpers import save_file

log = logging.getLogger(__name__)

SKIP_FILE = object()


class TildaArchive(object):
    def __init__(self, path):
        self.path = path

    def process(self):
        log.debug('processing archive file %s', self.path)

        with zipfile.ZipFile(self.path) as zf:
            for zipinfo in zf.infolist():
                log.debug('  file %s', zipinfo.filename)
                try:
                    # парсинг контента
                    self.process_file(zf, zipinfo)

                    # распаковка
                    with zf.open(zipinfo) as f:
                        save_as = self.extract_path(zipinfo)
                        if save_as != SKIP_FILE:
                            save_file(f, save_as)
                except Exception:
                    log.exception('Error in Tilda file processing')

        self.done()

    def process_file(self, zf, zipinfo):
        pass

    def extract_path(self, zipinfo):
        """
        Возвращает путь для распаковки каждого файла из архива
        """
        return SKIP_FILE

    def done(self):
        pass

    @staticmethod
    def strip_project(filename):
        return re.sub(r'project\d+/', '', filename).lstrip('/')

    @staticmethod
    def is_css(filename):
        # галерея зероблока кладет свои файлы в папку images - поддерживаем это
        return filename.startswith(('css/', 'images/')) and filename.endswith('.css')

    @staticmethod
    def is_js(filename):
        return filename.startswith(('js/', 'images/')) and filename.endswith('.js')

    @staticmethod
    def is_image(filename):
        return bool(re.match(r'(project\d+/)?images/[-a-z0-9_]+\.(png|jpg|jpeg|svg|gif)$', filename, re.I))


class IrkruTildaArchive(TildaArchive):
    def __init__(self, path, material):
        super(IrkruTildaArchive, self).__init__(path)
        self.material = material
        self.styles = None
        self.scripts = None
        self.body = None

    @property
    def extract_root(self):
        return self.material.tilda_extract_root

    def process_file(self, zf, zipinfo):
        """
        Из файла pagexxx.html выдирает ссылки на стили и скрипты, из файла pagexxbody
        берет хтмл-код для тела
        """
        filename = self.strip_project(zipinfo.filename)

        if re.match(r'page\d+.html$', filename):
            with zf.open(zipinfo) as f:
                html = f.read().decode('utf-8')
                self.styles, self.scripts = self.find_assets(html)
        elif re.match(r'files/page\d+body.html$', filename):
            with zf.open(zipinfo) as f:
                self.body = f.read().decode('utf-8')

    def comment_jquery(self):
        """
        Комментирует jquery в списке скриптов, потому что он конфликтует с нашим
        """
        pattern = r'jquery[-\.\d]*(\.min)?\.js'
        if self.scripts:
            for index, line in enumerate(self.scripts):
                if re.search(pattern, line):
                    self.scripts[index] = '<!--' + line + '-->'
                    break

    def extract_path(self, zipinfo):
        """
        Возвращает путь, по которому сохранить файл
        """
        filename = self.strip_project(zipinfo.filename)
        path = SKIP_FILE

        if self.is_css(filename) or self.is_js(filename) or self.is_image(filename):
            path = os.path.join(self.extract_root, filename)

        return path

    @staticmethod
    def find_assets(html, head_only=True):
        """
        Парсит содержимое файла pageXX.html и находит js и css в хеде
        """
        styles, scripts = None, None

        if head_only:
            i = html.find('<head>')
            j = html.find('</head>')
            if i == -1 or j == -1:
                return None, None
            html = html[i:j]  # оставим только head

        link_pattern = re.compile(r'''<link[^>]+rel=["']stylesheet["'].+?>''')
        styles = link_pattern.findall(html)

        link_pattern = re.compile(r'''<script.+?</script>''', re.DOTALL)
        scripts = link_pattern.findall(html)

        return styles, scripts

    def done(self):
        """
        Вызывается после обработки всех файлов
        """
        if self.styles:
            self.material.styles = '\n'.join(self.styles)

        if self.scripts:
            self.comment_jquery()
            self.material.scripts = '\n'.join(self.scripts)

        if self.body:
            self.material.tilda_content = self.body

        self.material.save()
