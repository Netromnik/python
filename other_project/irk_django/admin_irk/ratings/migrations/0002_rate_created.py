# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='created',
            field=models.DateTimeField(default=None, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f', auto_now_add=True),
            preserve_default=False,
        ),
    ]
