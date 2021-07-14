# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-08-06 04:15
from __future__ import unicode_literals

from django.db import migrations
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('special', '0003_auto_20200210_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='branding',
            field=irk.utils.fields.file.ImageRemovableField(default='', help_text='\u0420\u0430\u0437\u043c\u0435\u0440\u044b \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f: 1920\xd7600 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/special/branding', verbose_name='\u0411\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'),
            preserve_default=False,
        ),
    ]