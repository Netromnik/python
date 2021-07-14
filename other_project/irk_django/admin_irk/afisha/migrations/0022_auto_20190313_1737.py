# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0021_auto_20190305_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='fb_url',
            field=models.URLField(default=b'', verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 Facebook', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='inst_url',
            field=models.URLField(default=b'', verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 Instagram', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='ok_url',
            field=models.URLField(default=b'', verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u041e\u0434\u043d\u043e\u043a\u043b\u0430\u0441\u043d\u0438\u043a\u0438', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='vk_url',
            field=models.URLField(default=b'', verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0412\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0435', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='source_url',
            field=models.URLField(default=b'', verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0430\u0439\u0442', blank=True),
        ),
    ]
