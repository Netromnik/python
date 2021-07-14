# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import irk.news.models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0009_auto_20170712_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('link', models.URLField(verbose_name='\u0441\u0441\u044b\u043b\u043a\u0430')),
                ('_wide_image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('_standard_image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 705\u0445470. \u041f\u0440\u043e\u043f\u043e\u0440\u0446\u0438\u044f 3:2', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0421\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('number', models.PositiveSmallIntegerField(verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043f\u043e\u0434\u043a\u0430\u0441\u0442\u0430', null=True, editable=False)),
                ('introduction', models.CharField(max_length=1000, verbose_name='\u0412\u0432\u0435\u0434\u0435\u043d\u0438\u0435', blank=True)),
            ],
            options={
                'verbose_name': '\u043f\u043e\u0434\u043a\u0430\u0441\u0442',
                'verbose_name_plural': '\u043f\u043e\u0434\u043a\u0430\u0441\u0442\u044b',
            },
            bases=('news.basematerial',),
        ),
    ]
