# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-08-06 08:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0045_auto_20201130_1201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='is_bigfoot',
        ),
    ]