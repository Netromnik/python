# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file
import irk.adv.models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0007_auto_20180921_1126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='direct',
            name='client',
        ),
        migrations.RemoveField(
            model_name='direct',
            name='site',
        ),
        migrations.RemoveField(
            model_name='directperiod',
            name='direct',
        ),
        migrations.RemoveField(
            model_name='banner',
            name='all_sites',
        ),
        migrations.RemoveField(
            model_name='banner',
            name='place',
        ),
        migrations.AlterField(
            model_name='file',
            name='video',
            field=irk.utils.fields.file.FileRemovableField(help_text='\u041d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c \u0435\u0441\u043b\u0438 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043d WEBM', upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0412\u0438\u0434\u0435\u043e (mp4)', blank=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='video_webm',
            field=irk.utils.fields.file.FileRemovableField(help_text='\u041d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c \u0435\u0441\u043b\u0438 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043d MP4', upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0412\u0438\u0434\u0435\u043e (webm)', blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='booking_visible',
            field=models.BooleanField(default=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u0432 \u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438'),
        ),
        migrations.DeleteModel(
            name='Direct',
        ),
        migrations.DeleteModel(
            name='DirectPeriod',
        ),
    ]
