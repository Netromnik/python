# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import functools
import time
from contextlib import contextmanager

from django.db.backends import utils
from django.template import Template

try:
    import sqlparse
    sqlparse_format_kwargs_defaults = dict(
        reindent_aligned=True,
        truncate_strings=500,
    )
except ImportError:
    sqlparse = None

try:
    import pygments.lexers
    import pygments.formatters

    pygments_formatter = pygments.formatters.TerminalFormatter
    pygments_formatter_kwargs = {}
except ImportError:
    pygments = None

query_num = 0
class PrintQueryWrapper(utils.CursorDebugWrapper):
    """
    Отсюда: https://github.com/django-extensions/django-extensions/blob/master/django_extensions/management/commands/shell_plus.py#L444
    """
    def execute(self, sql, params=()):
        global query_num

        start_time = time.time()
        try:
            return utils.CursorWrapper.execute(self, sql, params)
        finally:
            query_num += 1
            execution_time = time.time() - start_time
            raw_sql = self.db.ops.last_executed_query(self.cursor, sql, params)

            if sqlparse:
                raw_sql = sqlparse.format(raw_sql, **sqlparse_format_kwargs_defaults)

            if pygments:
                raw_sql = pygments.highlight(
                    raw_sql,
                    pygments.lexers.get_lexer_by_name("sql"),
                    pygments_formatter(**pygments_formatter_kwargs),
                )

            print('{})\n{}'.format(query_num, raw_sql))
            print("")
            print('Execution time: %.3fs [Database: %s]' % (execution_time, self.db.alias))
            print("")


@contextmanager
def print_sql():
    """
    Хелпер печатает SQL-запросы, происходящие в его контексте

    >>> with print_sql():
    ...     # query orm here

    Работает только при DEBUG=True
    """
    global query_num

    query_num = 0
    old_wrapper = utils.CursorDebugWrapper
    try:
        utils.CursorDebugWrapper = PrintQueryWrapper
        yield
    finally:
        utils.CursorDebugWrapper = old_wrapper


def template_render_wrapper(func):
    """
    Враппер для функции Template.render

    Считает время выполнения рендеринга шаблонов
    https://github.com/orf/django-debug-toolbar-template-timings/blob/426d30c1608bccaba10ea53f82a5511967bf415e/template_timings_panel/panels/TemplateTimings.py#L96
    """
    @functools.wraps(func)
    def timing_hook(self, *args, **kwargs):
        print('[render] starting render {}'.format(self.origin))

        start_time = time.time()
        result = func(self, *args, **kwargs)
        time_taken = time.time() - start_time

        print('[render] {} done'.format(self.origin))
        print('[render] {:.3f} sec'.format(time_taken))
        print('')

        return result

    return timing_hook


@contextmanager
def print_render():
    """
    Хелпер для подсчета и логирования рендеринга шаблонов

    >>> with print_render():
    ...     html = render(request, 'home/index.html', context)
    """
    original_render = Template.render
    try:
        Template.render = template_render_wrapper(Template.render)
        yield
    finally:
        Template.render = original_render
