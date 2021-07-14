# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0006_auto_20170322_1523'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prism',
            name='klass',
        ),
        migrations.AddField(
            model_name='prism',
            name='icon',
            field=models.FileField(upload_to=b'img/site/afisha/prism', null=True, verbose_name='\u0438\u043a\u043e\u043d\u043a\u0430', blank=True),
        ),
    ]
