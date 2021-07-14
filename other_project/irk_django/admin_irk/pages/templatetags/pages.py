# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string

from irk.pages.models import Page


register = template.Library()


@register.tag
def page_menu(parser, token):
    """Это очень плохой и ужасный тег, и он передает в тег tasks.templatetags.task_menu текущую задачу

    {% page_menu %}
    {% page_menu 1 %}
    {% page_menu tpl.html %}
    {% page_menu 1 task=task %}
    """

    params = token.split_contents()

    try:
        max_level = params[1]
    except IndexError:
        max_level = 2

    task = None
    template = 'std_tree_menu.htm'
    for param in params[2:]:
        if '=' in param:
            task = param.split('=')[1]
        else:
            template = param.strip("'").strip('\'')

    return PageMenuNode(max_level=max_level, template=template, task=task)


class PageMenuNode(template.Node):
    MENU_TYPE_LIST = 'list'
    MENU_TYPE_TREE = 'tree'

    from_level = 1
    max_level = 2
    menu_type = MENU_TYPE_TREE
    template = ''

    def __init__(self, max_level, template, task=None):
        self.template = template
        self.max_level = int(max_level)
        self.task = task

    def render(self, context):
        request = context.get('request')
        site_url = request.path
        page_on = '/%s' % site_url.replace(request.csite.url, '')

        task = None
        if self.task:
            try:
                task = template.Variable(self.task).resolve(context)
            except (TypeError, template.VariableDoesNotExist):
                task = None

        menu = []
        levels = []
        clevel = self.from_level
        clevel_range = []
        ctree = menu
        levels.append(menu)
        root = None

        for page in Page.objects.filter(site=request.csite).order_by("position", "title"):
            level = len(page.url.strip("/").split("/"))
            if page.url != '/' and self.max_level >= level >= self.from_level:
                if self.menu_type == self.MENU_TYPE_TREE:
                    #  Построение меню в виде дерева.
                    if clevel == level:
                        pass
                    elif clevel < level:
                        if page_on == '/' or page.url[0:len(page_on)] != page_on:
                            continue
                        else:
                            ctree[len(ctree)-1]['on'] = True
                        # Если это следующий уровень
                        ctree = ctree[len(ctree)-1]['items']
                    else:
                        if clevel - level:
                            ctree = menu

                    ctree.append({
                        'page': page,
                        'items': [],
                    })
                else:
                    menu.append({
                        'page': page,
                        'level_next': level > clevel, 'level_prev': clevel > level,
                        'diff_level_range': range(0, abs(clevel - level))})
                clevel = level
                clevel_range = range(self.from_level-1, clevel)

        context = {
            'clevel_range': clevel_range,
            'task': task,
            'menu': menu,
            'request': request,
            'page_on': page_on,
            'levels': levels,
            'context': context,
            'site_url': site_url,
            'root': root,
            'clevel': clevel,
            'ctree': ctree,
        }

        return render_to_string(self.template, context)


@register.tag
def get_url(parser, token):
    params = token.split_contents()
    return PageUrlNode(params[1])


class PageUrlNode(template.Node):

    def __init__(self, page):
        self.page = template.Variable(page)

    def render(self, context):
        request = context.get('request')
        cpage = self.page.resolve(context)

        return "%s%s" % (request.csite.url, cpage.url.lstrip("/"))


class CurrentPageNode(template.Node):

    def __init__(self, variable):
        self.variable = variable

    def render(self, context):
        request = context.get('request')
        if not request:
            raise template.TemplateSyntaxError(u'В шаблоне недоступен объект request')

        try:
            page = Page.objects.get(url=request.path, site=request.csite)
        except Page.DoesNotExist:
            try:
                url = '/%s' % request.path.replace(request.csite.url, '')
            except AttributeError:
                page = None
            else:
                try:
                    page = Page.objects.get(url=url, site=request.csite)
                except Page.DoesNotExist:
                    page = None

        context[self.variable] = page

        return ''


@register.tag
def current_page(parser, token):
    """Flatpage для текущей страницы

    {% current_page as flatpage %}"""

    try:
        tag, _, variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'Tag current_page receives two arguments')

    return CurrentPageNode(variable)
