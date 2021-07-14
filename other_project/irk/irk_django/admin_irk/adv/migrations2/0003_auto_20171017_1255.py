# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0002_auto_20170418_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='invoice',
            field=models.CharField(default=b'', max_length=100, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0441\u0447\u0435\u0442\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='banner',
            name='is_payed',
            field=models.BooleanField(default=False, verbose_name='\u0421\u0447\u0435\u0442 \u043e\u043f\u043b\u0430\u0447\u0435\u043d'),
        ),
    ]
