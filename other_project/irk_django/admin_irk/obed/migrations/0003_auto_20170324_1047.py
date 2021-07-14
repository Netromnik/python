# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0002_auto_20161212_1624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='award',
            name='css_class',
        ),
        migrations.AddField(
            model_name='award',
            name='icon',
            field=models.FileField(upload_to=b'img/site/obed/award', null=True, verbose_name='\u0438\u043a\u043e\u043d\u043a\u0430', blank=True),
        ),
    ]
