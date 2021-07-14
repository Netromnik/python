# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.polls.views import quiz_read

urlpatterns = [
    # Опрос для Суши Студио
    url(r'^obed/japan_quiz/$', quiz_read, {'slug': 'sushi_studio_quiz', 'template': 'obed/quiz/sushi_studio.html'},
        name='sushi_studio_quiz'),
    # Партнерские опросы
    url(r'^news/fuel_quiz/$', quiz_read, {'slug': 'fuel_quiz', 'template': 'news-less/quiz/fuel.html'},
        name='fuel_quiz'),
    url(r'^news/landlord_quiz/$', quiz_read, {'slug': 'crystal_quiz', 'template': 'news-less/quiz/fuel.html'},
        name='crystal_quiz'),
    url(r'^news/house_quiz/$', quiz_read, {'slug': 'betonov_quiz', 'template': 'news-less/quiz/fuel.html'},
        name='betonov_quiz'),
]
