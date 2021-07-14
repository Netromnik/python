# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0004_barofest'),
    ]

    operations = [
        migrations.AddField(
            model_name='establishment',
            name='barofest_description',
            field=models.TextField(default=b'', verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True),
        ),
    ]
