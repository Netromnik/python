# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0013_scheduled_tasks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledtask',
            name='log',
            field=models.TextField(default=b'', verbose_name='\u041b\u043e\u0433 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f', blank=True),
        ),
        migrations.AlterField(
            model_name='scheduledtask',
            name='when',
            field=models.DateTimeField(verbose_name='\u0414\u043e\u043b\u0436\u043d\u0430 \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c\u0441\u044f'),
        ),
    ]
