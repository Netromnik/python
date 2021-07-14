# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


DATA = {
    'fuel_quiz': {
        'title': 'Довольны ли вы качеством обслуживания на АЗС?',
        'content': '<p>Современного человека сложно представить без автомобиля.<br>'
                   'В Иркутской области много автомобилистов и автозаправок.<br>'
                   'Нам хотелось бы узнать ваше мнение о качестве обслуживания на АЗС Иркутской области.</p>'
    },
    'crystal_quiz': {
        'title': 'Загородный дом или квартира в городе?',
        'content': ''
    },
    'sushi_studio_quiz': {
        'title': 'Опрос для любителей японской кухни',
        'content': ''
    },
    'betonov_quiz': {
        'title': 'Из чего строить дом?',
        'content': ''
    },
}


def forwards(apps, schema_editor):
    Quiz = apps.get_model('polls', 'Quiz')

    for slug, data in DATA.items():
        Quiz.objects.filter(slug=slug).update(title=data['title'], content=data['content'])


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20170406_1658'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
