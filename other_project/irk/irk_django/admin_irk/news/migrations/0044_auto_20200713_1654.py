# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-13 16:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0043_postmeta_covidpage_20200403_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tildaarticle',
            name='basematerial_ptr',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='news_tildaarticle_related', serialize=False, to='news.BaseMaterial'),
        ),
    ]