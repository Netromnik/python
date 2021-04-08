import django_tables2 as tables
from django.utils.html import format_html
from fsm.stat_logick import dispath
from fsm.models import Task

_go = '<a href="/ticket/{}" class="btn btn-primary btn-sm" role="button" aria-pressed="true">перейти</a>'
_template_disp = '<a href="{}" class="btn btn-primary btn-sm btn-up" role="button" aria-pressed="true">{}</a>'
_get = '<a href="/ticket/api/{}/up/" class="btn btn-primary btn-sm btn-up" role="button" aria-pressed="true">Взять</a>'
_put = '<a href="/ticket/api/{}/re_open/" class="btn btn-primary btn-sm btn-up" role="button" aria-pressed="true">Переоткрыть</a>'

class NonSubscriteTaskButton(tables.Column):
    def render(self, value):
        task = Task.object.get(id=value)
        d= dispath(task.state, "responsible", task.pk)
        btn = []
        btn.append(_go.format(value))
        btn +=[format_html(_template_disp, i.href, i.name) for i in d]
        return format_html("".join(btn))
        # return format_html(
        #     _go+_get,value,value)

class TaskActiveButton(tables.Column):
    def render(self, value):
        task = Task.object.get(id=value)
        d= dispath(task.state, "responsible", task.pk)
        btn = []
        btn.append(_go.format(value))
        btn +=[format_html(_template_disp, i.href, i.name) for i in d]
        return format_html("".join(btn))

class AdminButton(tables.Column):
    def render(self, value):
        return format_html(_go+_put,value,value)

class TimeDateColl(tables.Column):
    def render(self, value):
        return format_html(value.strftime("%d-%m-%Y"))