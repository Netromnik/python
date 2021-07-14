# -*- coding: utf-8 -*-

import logging
import sys
import os
import re
import requests

from urlparse import urljoin, urlparse
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Архиватор legacy разделов

    Примеры использования::
        manage.py legacy_archive 2014 '/2014/' disable_form: архивирование раздела.
        Первый параметр - имя папки раздела
        Второй параметр - url архивируемого раздела
        disable_form - добавить disable полям форм (необязательный параметр)
    """

    archive_path = settings.ARCHIVE_LEGACY_PATH
    asset_url_start = '/legacy/{0}/'
    html_path = ''
    asset_path = ''
    start_url = ''
    disable_form = False
    parsed_htmls = []
    saved_assets = []

    def add_arguments(self, parser):
        parser.add_argument('slug', help='Slug', type=str)
        parser.add_argument('url', help='Url', type=str)

    def handle(self, *args, **options):

        try:
            slug = options['slug']
            self.archive_path = os.path.join(self.archive_path, slug)
            if not os.path.exists(self.archive_path):
                os.makedirs(self.archive_path)
        except IndexError:
            print u'Не заполнен slug'
            sys.exit()

        self.html_path = os.path.join(self.archive_path, 'html/')
        self.asset_path = os.path.join(self.archive_path, 'assets/')

        try:
            self.start_url = options['url']
        except IndexError:
            print u'Не заполнен url'
            sys.exit()

        try:
            if args[2] == 'disable_form':
                self.disable_form = True
        except IndexError:
            pass

        self.asset_url_start = self.asset_url_start.format(slug)

        link = self.absolute_url(self.start_url)
        self.download_html(link)

    def download_html(self, link):
        """ Скачивание html страниц """

        url = urlparse(link)

        # Скачивать страницы только выбранного раздела
        if link in self.parsed_htmls or not url.path.startswith(self.start_url):
            return False

        # Скачивание страницы
        logger.debug('Download page {0}'.format(link))
        content = requests.get(link, allow_redirects=True).content
        self.parsed_htmls.append(link)

        # Создание полного пути до файла
        url = urlparse(link)
        path = os.path.join(self.html_path, url.path.lstrip('/'))
        params_str = ''
        if url.query:
            params_str = '_{0}'.format(url.query)
        paths = path.strip("/").split('/')
        file_path = '/{0}'.format('/'.join(paths[:-1]))
        file_name = '{0}/{1}{2}.html'.format(file_path, paths[-1], params_str)

        # Получение ссылок на медиа файлы
        asset_urls = self.find_assets(content)

        # Замена url до медиа файлов в html
        content = self.replace_assets_url(asset_urls, content)

        # Добавление disable полям форм
        if self.disable_form:
            content = self.disable_firm_tags(content)

        # Получение ссылок на связанные страницы
        a_urls = self.find_href(content)

        # Сохранение файла
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(file_name, 'wb') as fd:
            content_relative_url = content.replace('http://{0}'.format(settings.BASE_HOST), '').\
                replace('http://www.{0}'.format(settings.BASE_HOST), '')
            fd.write(content_relative_url)

        # Скачивание медиа файлов
        for asset_url in asset_urls:
            self.download_asset(asset_url)

        for a_url in a_urls:
            a_url = self.absolute_url(a_url, link)
            self.download_html(a_url)

    def download_asset(self, link):
        """ Скачивание медиа файлов """

        link = self.absolute_url(link)
        if link in self.saved_assets:
            return False

        # Скачивание медиа файла
        logger.debug('Download asset {0}'.format(link))
        content = requests.get(link, allow_redirects=True).content
        self.saved_assets.append(link)

        # Создание полного пути до файла
        url = urlparse(link)
        path = os.path.join(self.asset_path, url.path.lstrip('/'))
        paths = path.strip("/").split('/')
        file_path = '/{0}'.format('/'.join(paths[:-1]))
        file_name = '{0}/{1}'.format(file_path, paths[-1])
        file_path = os.path.dirname(file_name)

        # Скачивание медиа файлов из css файлов
        _, ext = os.path.splitext(file_name)
        if ext == '.css':
            assets_urls = self.find_assets(content)
            content = self.replace_assets_url(assets_urls, content)
            for asset_url in assets_urls:
                self.download_asset(asset_url)

        # Сохранение файла
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(file_name, 'wb') as fd:
            content_relative_url = content.replace('http://{0}'.format(settings.BASE_HOST), '').\
                replace('http://www.{0}'.format(settings.BASE_HOST), '')
            fd.write(content_relative_url)

    def absolute_url(self, url, parent_url=None):
        """ Превращение относительной ссылки в абсолютную """

        url = url.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"') \
            .replace('&#39;', "'")
        url = url.replace('../', '')
        if url.startswith('./') and parent_url:
            url_obj = urlparse(parent_url)
            url = url.replace('./', url_obj.path)
        if url.startswith('https://'):
            url = url.replace('https://', 'http://')
        if not url.startswith('http://'):
            url = urljoin('http://{0}/'.format(settings.BASE_HOST), url)
        return url

    def disable_firm_tags(self, content):
        """ Добавление disable полям форм """

        for tag in ['button', 'fieldset', 'form', 'input', 'option', 'textarea']:
            content = content.replace('<{0}'.format(tag), '<{0} disabled '.format(tag))
        return content

    def replace_assets_url(self, links, content):
        """ Замена ссылок до медиа файлов новыми путями """

        for link in links:
            url = urlparse(link)
            link_new = urljoin(self.asset_url_start, url.path.lstrip('/'))
            content = content.replace(link, link_new)
        return content

    def find_href(self, content):
        """ Поиск ссылок на html страницы в контенте"""

        a_p = re.compile('<a\s([^>]+)>')
        href_p = re.compile('href=([^\s]+)')
        urls = []
        a_list = list(set(a_p.findall(content)))
        for a_item in a_list:
            a_item = a_item.replace('"', '').replace("'", '')
            try:
                urls.append(href_p.search(a_item).group(1))
            except AttributeError:
                pass
        return urls

    def find_assets(self, content):
        """ Поиск ссылок на медиа файлы в контенте"""
        p = re.compile('(?:=|=\s|load:\s|url|url\()(?:\"|\'|\()([^\"\'\(]+\.(?:png|jpeg|jpg|gif|css|js|swf|bmp|ico|less|ttf|woff|eot))')
        links = list(set(p.findall(content)))
        links = [x for x in links if 'base64' not in x]
        return links
