# coding=utf-8
import pytest
import re
from mock import patch

from irk.utils.files import staticfiles


@pytest.fixture
def storage():
    return staticfiles.IrkruManifestStaticFilesStorage()


def test(storage):

    converter = storage.url_converter('anywhere/style.css', {})
    assert callable(converter)

    template = 'url("%s")'
    name = 'css/compiled/compile/style2.css'
    str = 'url("/static/img/shadow/hint-r.png")'

    # стандартный паттерн, которым джанга ищет юрля для замены в css-файлах
    PATTERN = r"""(url\(['"]{0,1}\s*(.*?)["']{0,1}\))"""

    # стандартный сторадж

    # в относительных адресах он просто заменяет файл на хэшированный файл
    m = re.match(PATTERN, 'url(img/4.gif)')
    with patch.object(storage, 'hashed_name') as hashed_name:
        hashed_name.return_value = 'img/4.8bce7d03204b.gif'
        result = converter(m)
        assert result == 'url("img/4.8bce7d03204b.gif")'

    # абсолютные он не трогает
    m = re.match(PATTERN, 'url(/img/4.gif)')
    result = converter(m)
    assert result == 'url(/img/4.gif)'

    # всякие data-url тоже не трогает
    m = re.match(PATTERN, 'url(data:image/svg)')
    result = converter(m)
    assert result == 'url(data:image/svg)'

    # совсем абсолютные тоже не трогает
    m = re.match(PATTERN, 'url(http://some)')
    result = converter(m)
    assert result == 'url(http://some)'

    # у нас, в отличае от стандартного обработчика, все пути к статике
    # записаны как /static/file.jpg - это позволяет сервить статику во время
    # разработки. Но при подготовке файлов к деплою через collectstatic,
    # нам нужно вырезать этот префикс и поправить путь на относительный (или абсолютный)

    # корректно обрабатывать путь, начинающийся со /static/

    converter = storage.url_converter('img/style.css', {})
    m = re.match(PATTERN, 'url(/static/img/4.gif)')
    with patch.object(storage, 'hashed_name') as hashed_name:
        hashed_name.return_value = 'img/4.8bce7d03204b.gif'
        result = converter(m)
        assert result == 'url("4.8bce7d03204b.gif")'

    # мы в файле css/404.css
    converter = storage.url_converter('css/404.css', {})
    # видим строку от корня
    m = re.match(PATTERN, "url('/static/img/404/grass.jpg')")
    with patch.object(storage, 'hashed_name') as hashed_name:
        hashed_name.return_value = 'img/404/grass.5859846686ca.jpg'
        result = converter(m)
        assert result == 'url("../img/404/grass.5859846686ca.jpg")'


def test_relative(storage):
    assert storage.relative('style.css', '1.gif') == '1.gif'
    assert storage.relative('common/style.css', 'common/1.gif') == '1.gif'
    assert storage.relative('style.css', 'common/1.gif') == 'common/1.gif'
    assert storage.relative('common/style.css', 'lib/1.gif') == '../lib/1.gif'
