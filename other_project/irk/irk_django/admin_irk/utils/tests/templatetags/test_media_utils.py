# coding=utf-8
from __future__ import unicode_literals

import pytest
from django.template import Template, Context


class TestLessTag:

    def render_less(self, less_file):
        template = Template("{{% load media_utils %}}{{% less '{}' %}}".format(less_file))
        return template.render(Context())

    def test_should_give_css_if_not_debug(self, settings):
        """Cуществующий файл заменяется на скомпилированный css"""

        settings.DEBUG_LESS = False
        settings.STATIC_URL = '/static/'

        less_file = '/less/compile/apps/about.less'
        expected = 'href="/static/css/compiled/compile/apps/about.css"'

        result = self.render_less(less_file)
        assert expected in result

    def test_should_return_less_if_debug(self, settings):
        """Существующий файл в режиме разработки - просто сервится из статики"""

        settings.DEBUG_LESS = True
        settings.STATIC_URL = '/static/'

        result = self.render_less('/less/compile/apps/about.less')
        expected = '"/static/less/compile/apps/about.less"'

        assert expected in result

    def test_should_raise_error_on_nonexisting_file(self, settings):
        """Несуществующий файл дает ошибку при дебаге"""

        settings.DEBUG_LESS = True

        with pytest.raises(ValueError):
            self.render_less('nonexistant.less')

    def test_should_return_empty_string_if_not_debug(self, settings):
        """Несуществующий файл дает пустую строку на проде"""

        settings.DEBUG_LESS = False
        assert self.render_less('nonexistant.less') == ''

    def test_should_cache_calls(self, settings):
        """Повторные вызовы дают информацию из кеша на проде"""

        settings.DEBUG_LESS = False
        a = self.render_less('/less/compile/apps/about.less')
        b = self.render_less('/less/compile/apps/about.less')

        from irk.utils.templatetags.media_utils import cache
        assert len(cache) == 1
        assert a == b
