# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-10 15:15
from __future__ import unicode_literals

from django.db import migrations
import irk.utils.fields.file
import irk.utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('landings', '0006_auto_20200122_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='attach',
            field=irk.utils.fields.file.FileRemovableField(blank=True, null=True, upload_to='img/site/landings/attach/', validators=[irk.utils.validators.FileSizeValidator(max_size=10485760)], verbose_name='\u041f\u0440\u0438\u043a\u0440\u0435\u043f\u043b\u0435\u043d\u043d\u044b\u0439 \u0444\u0430\u0439\u043b'),
        ),
    ]
