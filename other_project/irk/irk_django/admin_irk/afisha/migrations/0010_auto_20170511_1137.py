# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0009_auto_20170418_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kinomaxevent',
            name='image',
            field=models.URLField(null=True, verbose_name='\u0430\u0434\u0440\u0435\u0441 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='kinomaxevent',
            name='trailer',
            field=models.URLField(null=True, verbose_name='\u0442\u0440\u0435\u0439\u043b\u0435\u0440'),
        ),
    ]
