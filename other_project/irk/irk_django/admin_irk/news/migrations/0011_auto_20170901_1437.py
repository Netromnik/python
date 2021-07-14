# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0010_news_has_audio'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoinRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stamp', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('btc', models.FloatField(verbose_name='Bitcoin', blank=True)),
                ('eth', models.FloatField(verbose_name='Ethereum', blank=True)),
                ('xrp', models.FloatField(verbose_name='Ripple', blank=True)),
            ],
            options={
                'verbose_name': '\u043a\u0443\u0440\u0441\u044b \u043a\u0440\u0438\u043f\u0442\u043e\u0432\u0430\u043b\u044e\u0442',
                'verbose_name_plural': '\u043a\u0443\u0440\u0441\u044b \u043a\u0440\u0438\u043f\u0442\u043e\u0432\u0430\u043b\u044e\u0442',
            },
        ),
    ]
