# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landings', '0002_treasuredish'),
    ]

    operations = [
        migrations.AddField(
            model_name='treasuredish',
            name='name_en',
            field=models.CharField(default='', max_length=255, verbose_name='\u0410\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True),
        ),
    ]
