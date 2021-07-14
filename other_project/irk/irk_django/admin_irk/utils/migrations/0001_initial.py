# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TweetEmbed',
            fields=[
                ('id', models.BigIntegerField(serialize=False, verbose_name='Tweet ID', primary_key=True)),
                ('url', models.URLField(verbose_name='Tweet URL')),
                ('html', models.TextField(verbose_name='HTML-\u043a\u043e\u0434', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='VkVideoEmbed',
            fields=[
                ('id', models.CharField(max_length=20, serialize=False, verbose_name='Vk video ID', primary_key=True)),
                ('url', models.URLField(verbose_name='Video URL')),
                ('html', models.TextField(verbose_name='HTML-\u043a\u043e\u0434', blank=True)),
            ],
        ),
    ]
