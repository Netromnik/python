# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0015_auto_20170714_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='guide',
            name='price_description',
            field=models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0434\u043b\u044f \u0446\u0435\u043d\u044b', blank=True),
        ),
    ]
