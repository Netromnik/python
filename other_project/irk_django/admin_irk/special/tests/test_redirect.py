# coding=utf-8
import datetime

import pytest
from ddf import G
from django.contrib.contenttypes.models import ContentType

from irk.news.models import Article
from irk.special.models import Project

INDEXES = [
    ('/afisha/film/', '/special/film/'),
    ('/afisha/jazz/', '/special/jazz/'),
    ('/obed/columnist/', '/special/columnist/'),
    ('/tourism/abroad/', '/special/abroad/'),
    ('/tourism/club/', '/special/club/'),
    ('/news/9may/', '/special/9may/'),
    ('/news/9may/article/', '/special/9may/'),
    ('/news/9may/photo/', '/special/9may/'),
    ('/news/9may/video/', '/special/9may/'),
    ('/news/9may/graphics/', '/special/9may/'),
]


@pytest.mark.parametrize('old,new', INDEXES)
@pytest.mark.django_db
def test_redirect(client, old, new):
    response = client.get('/news/9may/')
    assert response.status_code == 301
    assert response.url == '/special/9may/'


# вьюшки

@pytest.mark.django_db
def test_redirect_read(client, news_article):
    url = '/news/9may/article/{}/'.format(news_article.id)
    to = '/news/articles/20200813/some/'

    response = client.get(url)
    assert response.status_code == 301
    assert response.url == to


@pytest.fixture
def news_article(transactional_db):

    project = G(Project, slug='9may')
    article = G(Article, stamp=datetime.datetime(2020, 8, 13), slug='some', is_hidden=False, project=project)

    # почему-то content_type сам не присваивается в методе save (там pk стоит), добавим его вручную
    article.content_type = ContentType.objects.get_for_model(Article, for_concrete_model=False)
    article.save()

    return article

# мне пришлось помучиться, чтобы создать базу
# сначала я удалил test_irk
# потом отключил в конфиге кодировку и создал pytest - дошел до ошибки
# потом переключил в конфиге charset: utf8mb4 и снова запустил - заработало
