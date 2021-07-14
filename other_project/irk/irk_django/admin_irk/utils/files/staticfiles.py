# -*- coding: utf-8 -*-

import logging
import os

from django.contrib.staticfiles.storage import StaticFilesStorage, ManifestStaticFilesStorage
from django.conf import settings


logger = logging.getLogger(__name__)


class IrkruManifestStaticFilesStorage(ManifestStaticFilesStorage):
    def url(self, name, force=False):
        """
        Возвращает URL к файлу статики

        Наша модифициаци отличается от стандартной тем, что не выдает ValueError, если
        статичный файл не найден в манифесте. В этом случае мы просто отдаем путь к нехешированной
        версии файла "как есть". Поэтому сайт не падает, если какой-то файл статики
        не выложился на сервер.
        """
        try:
            return self._url(self.stored_name, name, force)
        except ValueError as err:
            logger.error('Static file %s not found: %s', name, err)
            # вернем просто http://STATIC_URL + name
            return StaticFilesStorage().url(name)

    def url_converter(self, name, hashed_files, template=None):
        """
        Эта функция вызывается на этапе `collectstatic` и меняет адреса внутри инклудов
        в css-файлах. Например: background: url(/static/img/4.gif)

        У нас все адреса в статике записаны как /static/file.jpg. Это позволяет нам
        решить две задачи:

        1) статика сервится при разработке через runserver без проблем;
        2) проще адресация - не нужно высчитывать относительные пути.

        Но минус в том, что стандартный collectstatic не проглотит такие адреса. Поэтому
        мы вырезаем префикс /static/ и заменяем адрес на относительный - будто так и было.

        Еще одни плюс относительных адресов - файлы можно выложить на любой сервер в любую
        папку и все будет работать.
        """
        if template is None:
            template = self.default_template

        original_converter = super(IrkruManifestStaticFilesStorage, self) \
            .url_converter(name, hashed_files, template)

        def converter(matchobj):
            matched, url = matchobj.groups()

            if url.startswith('/static/'):
                target = url[8:]
                # заменим путь от корня на относительный (зная, что мы в файле name)
                # url(/static/img/4.gif) -> url(../img/4.gif)
                url = self.relative(name, target)

            # подменим оригинальный matchobject
            class MatchObjectMock(object):
                def groups(self):
                    return matched, url

            # а дальше джанга сама заменит файл на хешированный:
            # url(../img/4.gif) -> url(../img/4.ab44a3d.gif)
            return original_converter(MatchObjectMock())

        return converter

    def relative(self, startfile, targetfile):
        """
        Вычисляет относительный путь от startfile к targetfile
        """
        if startfile.startswith('/') or targetfile.startswith('/'):
            raise ValueError(
                u'Функция relative работает только с относительными путями, '
                u'startfile: "{}", targetfile: "{}"'.format(startfile, targetfile)
            )
        startdir = os.path.dirname(startfile)
        return os.path.relpath(targetfile, startdir)
