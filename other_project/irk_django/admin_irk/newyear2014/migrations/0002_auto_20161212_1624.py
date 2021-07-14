# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newyear2014', '0001_initial'),
        ('news', '0002_auto_20161212_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
            ],
            options={
                'verbose_name': '\u0441\u0442\u0430\u0442\u044c\u044f',
                'proxy': True,
                'verbose_name_plural': '\u0441\u0442\u0430\u0442\u044c\u0438 \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('news.article',),
        ),
        migrations.CreateModel(
            name='Infographic',
            fields=[
            ],
            options={
                'verbose_name': '\u0438\u043d\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430',
                'proxy': True,
                'verbose_name_plural': '\u0438\u043d\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430 \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('news.infographic',),
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
            ],
            options={
                'verbose_name': '\u0444\u043e\u0442\u043e\u0440\u0435\u043f\u043e\u0440\u0442\u0430\u0436',
                'proxy': True,
                'verbose_name_plural': '\u0444\u043e\u0442\u043e\u0440\u0435\u043f\u043e\u0440\u0442\u0430\u0436\u0438 \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('news.photo',),
        ),
        migrations.AddField(
            model_name='zodiac',
            name='horoscope',
            field=models.ForeignKey(verbose_name='\u0413\u043e\u0440\u043e\u0441\u043a\u043e\u043f', to='newyear2014.Horoscope'),
        ),
        migrations.AddField(
            model_name='wish',
            name='user',
            field=models.ForeignKey(related_name='wish', verbose_name='\u0410\u0432\u0442\u043e\u0440 \u0436\u0435\u043b\u0430\u043d\u0438\u044f', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='textcontestparticipant',
            name='contest',
            field=models.ForeignKey(related_name='participants', to='newyear2014.TextContest'),
        ),
        migrations.AddField(
            model_name='textcontestparticipant',
            name='user',
            field=models.ForeignKey(related_name='text_contests', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='user',
            field=models.ForeignKey(related_name='prediction_question', verbose_name='\u0410\u0432\u0442\u043e\u0440 \u0432\u043e\u043f\u0440\u043e\u0441\u0430', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='photocontestparticipant',
            name='contest',
            field=models.ForeignKey(related_name='participants', to='newyear2014.PhotoContest'),
        ),
        migrations.AddField(
            model_name='photocontestparticipant',
            name='user',
            field=models.ForeignKey(related_name='photo_contests', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='congratulation',
            name='user',
            field=models.ForeignKey(related_name='congratulation', verbose_name='\u0410\u0432\u0442\u043e\u0440 \u043f\u043e\u0437\u0434\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
