# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-11-22 12:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import irk.news.models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0031_postmeta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='bigfoot_image',
            field=models.ImageField(blank=True, help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 1920\u0445600 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0424\u043e\u043d\u043e\u0432\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f \u0448\u0430\u043f\u043a\u0438'),
        ),
        migrations.RenameField(
            model_name='article',
            old_name='bigfoot_image',
            new_name='header_image',
        ),
    ]
