# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file
import irk.adv.models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0003_auto_20171017_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='show_player',
            field=models.BooleanField(default=False, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u0432\u0438\u0434\u0435\u043e-\u043f\u043b\u044d\u0439\u0435\u0440'),
        ),
        migrations.AddField(
            model_name='file',
            name='video_webm',
            field=irk.utils.fields.file.FileRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0412\u0438\u0434\u0435\u043e (webm)', blank=True),
        ),
    ]
