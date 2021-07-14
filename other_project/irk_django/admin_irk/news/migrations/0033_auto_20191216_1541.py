# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-12-16 15:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import irk.news.models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0032_rename_bigfoot_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='is_visible',
            field=models.BooleanField(db_index=True, default=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c'),
        ),
    ]