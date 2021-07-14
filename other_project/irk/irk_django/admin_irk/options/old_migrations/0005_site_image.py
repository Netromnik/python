# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-04 11:25
from __future__ import unicode_literals

from django.db import migrations
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0004_auto_20200210_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='image',
            field=irk.utils.fields.file.FileRemovableField(blank=True, help_text='\u0420\u0430\u0437\u043c\u0435\u0440 \u043f\u043e \u0432\u044b\u0441\u043e\u0442\u0435 20px. \u041c\u043e\u0436\u043d\u043e SVG. \u0417\u0430\u043c\u0435\u043d\u044f\u0435\u0442 \u0442\u0435\u043a\u0441\u0442 \u0432 \u043c\u0435\u043d\u044e \u043a\u0430\u0440\u0442\u0438\u043d\u043a\u043e\u0439', null=True, upload_to=b'img/site/option/image/', verbose_name='\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430 \u0432\u043c\u0435\u0441\u0442\u043e \u0442\u0435\u043a\u0441\u0442\u0430'),
        ),
    ]