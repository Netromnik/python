# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-04 15:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0027_auto_20201204_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ramblerevent',
            name='creator_name',
            field=models.CharField(max_length=1000, verbose_name='\u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e'),
        ),
        migrations.AlterField(
            model_name='ramblerevent',
            name='description',
            field=models.CharField(max_length=10000, verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='ramblerevent',
            name='director',
            field=models.CharField(max_length=1000, verbose_name='\u0440\u0435\u0436\u0438\u0441\u0435\u0440'),
        ),
    ]
