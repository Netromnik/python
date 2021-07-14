# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-03 14:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('landings', '0008_covidpage'),
        ('news', '0042_utf8mb4_support'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmeta',
            name='landings_covidpage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='postmeta', to='landings.CovidPage'),
        ),
        migrations.AlterField(
            model_name='postmeta',
            name='material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='postmeta', to='news.BaseMaterial'),
        ),
    ]
