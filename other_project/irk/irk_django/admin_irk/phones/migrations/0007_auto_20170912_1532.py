# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0006_auto_20170220_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='firms',
            name='wide_image',
            field=irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/phones/wide/', null=True, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True),
        ),
    ]
