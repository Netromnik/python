# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-09 23:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagramtag',
            name='name',
            field=models.CharField(help_text='\u0431\u0435\u0437 #', max_length=191, unique=True, verbose_name='\u0422\u0435\u0433'),
        ),
        migrations.AlterField(
            model_name='instagramtag',
            name='title',
            field=models.CharField(max_length=191, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435'),
        ),
    ]
