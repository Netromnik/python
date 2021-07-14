# -*- coding: utf-8 -*-

import json
import urllib
import urlparse
import StringIO

from django.conf import settings
from django.http import HttpResponse
from django.views.generic.base import View
from django.utils.xmlutils import SimplerXMLGenerator
from django.contrib.sites.models import Site

from irk.utils.files.helpers import static_link


class BaseOpenSearchView(View):
    """Базовый класс для OpenSearch поиска"""

    short_name = u''
    description = u''
    use_suggestions = False

    def get_url(self):
        """Ссылка для результатов поиска

        Должна быть относительной и иметь параметр {searchTerms},
        например `/news/search/?q={searchTerms}`
        """

        raise NotImplementedError()

    def get_suggestions(self, term):
        """Поиск может предлагать пользователю на выбор варианты для поиска

        Метод должен возвращать итерабельный объект с строками в нем.
        Не забыть сделать атрибут класса `use_suggestions = True` при переопределении этого метода"""

        raise NotImplementedError()

    def get(self, request):
        response = HttpResponse()

        action = request.GET.get('action')
        if action == 'suggestions' and self.use_suggestions:
            query = request.GET.get('q', '')
            response['Content-Type'] = 'application/x-suggestions+json'
            response.write(json.dumps([
                query,
                self.get_suggestions(query),
            ]))
        else:
            response['Content-Type'] = 'text/xml'
            self.write(response)

        return response

    def write(self, outfile, encoding='utf-8'):
        site = Site.objects.get_current()
        protocol = 'https://' if settings.FORCE_HTTPS else 'http://'
        base_url = ''.join([protocol, site.domain])

        handler = SimplerXMLGenerator(outfile, encoding)
        handler.startDocument()

        # Корневой элемент
        doc_attrs = {
            'xmlns': 'http://a9.com/-/spec/opensearch/1.1/',
            'xmlns:referrer': 'http://a9.com/-/opensearch/extensions/referrer/1.0/',
        }
        if self.use_suggestions:
            doc_attrs['xmlns:suggestions'] = 'http://www.opensearch.org/specifications/opensearch/extensions/suggestions/1.1'
        handler.startElement('OpenSearchDescription', doc_attrs)

        # Описание
        if self.short_name:
            handler.addQuickElement('ShortName', self.short_name)
        if self.description:
            handler.addQuickElement('Description', self.description)

        # Добавляем в ссылку параметр с плейсхолдером для реферера
        url = urlparse.urljoin(base_url, self.get_url())
        bits = list(urlparse.urlparse(url))
        query = {
            'ref': '{referrer:source?}',
        }
        for k, v in urlparse.parse_qs(bits[4]).items():
            query[k] = v[0]

        bits[4] = urllib.urlencode(query)
        url = urllib.unquote(urlparse.urlunparse(bits))

        handler.addQuickElement('Language', settings.LANGUAGE_CODE)

        handler.addQuickElement('Url', attrs={
            'type': 'text/html',
            'method': 'get',
            'template': url,
        })

        if self.use_suggestions:
            handler.addQuickElement('Url', attrs={
                'type': 'application/x-suggestions+json',
                'template': '{}{}?action=suggestions&q={{searchTerms}}'.format(base_url, self.request.path),
            })

        # Изображения
        handler.addQuickElement('Image', urlparse.urljoin(base_url, static_link('img/favicon.ico')), attrs={
            'height': '16',
            'width': '16',
            'type': 'image/x-icon',
        })
        handler.addQuickElement('Image', urlparse.urljoin(base_url, static_link('img/irkru-64x64.png')), attrs={
            'height': '64',
            'width': '64',
            'type': 'image/png',
        })

        handler.endElement('OpenSearchDescription')

    def write_string(self, encoding='utf-8'):
        s = StringIO.StringIO()
        self.write(s, encoding)

        return s.getvalue()
