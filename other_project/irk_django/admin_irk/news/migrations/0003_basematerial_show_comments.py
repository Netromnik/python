# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20161212_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='basematerial',
            name='show_comments',
            field=models.BooleanField(default=True, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438'),
        ),
    ]
