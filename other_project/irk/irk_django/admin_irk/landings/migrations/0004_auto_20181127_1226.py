# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landings', '0003_treasuredish_name_en'),
    ]

    operations = [
        migrations.AddField(
            model_name='treasuredish',
            name='position',
            field=models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', db_index=True),
        ),
        migrations.AddField(
            model_name='treasuredish',
            name='rating',
            field=models.PositiveSmallIntegerField(default=0, help_text='\u043e\u0442 1 \u0434\u043e 5'),
        ),
    ]
