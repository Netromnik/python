# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramEmbed',
            fields=[
                ('id', models.CharField(max_length=200, serialize=False, verbose_name='Slug', primary_key=True)),
                ('url', models.URLField()),
                ('html', models.TextField(verbose_name='HTML-\u043a\u043e\u0434', blank=True)),
            ],
        ),
    ]
