# coding=utf-8
from __future__ import absolute_import, unicode_literals

import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from irk.news.models import Article
from irk.recycle.models import Category, RelatedArticle
from irk.utils.http import JsonResponse


@login_required
def categories(request):
    """
    Отдает категории для списка сортировки
    """
    categories = []
    for cat in Category.objects.order_by('order'):
        cat_item = {
            'id': cat.id,
            'name': cat.name,
            'icon_class': cat.icon_class,
        }
        categories.append(cat_item)

    return JsonResponse(categories)


@login_required
def save_order(request):
    """
    Сохраняет порядок сортировки
    """
    new_order = request.GET.get('new_order')
    if new_order:
        new_order = json.loads(new_order)
        for item in new_order:
            cat = Category.objects.get(id=item['id'])
            cat.order = int(item['order'])
            cat.save()

        return HttpResponse('ok')

    return HttpResponse('Error')


@login_required
def article(request):
    """
    Отдает статьи по названию
    """
    search_name = request.GET.get('name')
    result = []
    query = Article.objects.filter(stamp__gte = '2015-1-1').filter(title__icontains = search_name).order_by('-stamp')
    for material in query:
        result.append({
            'id': material.id,
            'title': material.title,
            'link': str(material.get_absolute_url()),
        })

    return JsonResponse(result[:30])


@login_required
def change_article_status(request):
    """
    Добавляет или удаляет статью
    """
    action = request.GET.get('action')
    if action == 'Add':
        if len(RelatedArticle.objects.filter(article__id=request.GET.get('id'))) == 0:
            new_article = Article.objects.get(id=request.GET.get('id'))
            new_text = RelatedArticle(article = new_article)
            new_text.save()
            return HttpResponse('ok')
        return HttpResponse('Has already')

    elif action == 'Delete' and len(RelatedArticle.objects.filter(article__id=request.GET.get('id'))):
        del_article = RelatedArticle.objects.filter(article__id=request.GET.get('id'))
        del_article.delete()
        return HttpResponse('ok')


@login_required
def added_article(request):
    """
    Возвращает список всех добавленных раннее статей
    """
    result = []
    for art in RelatedArticle.objects.order_by('id'):
        result.append({
            'id': art.article.id,
            'title': art.article.title,
            'link': str(art.article.get_absolute_url()),
        })

    return JsonResponse(result)
