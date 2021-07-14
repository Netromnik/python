# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0003_auto_20181211_1145'),
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='layer',
            name='author',
        ),
        migrations.RemoveField(
            model_name='route',
            name='author',
        ),
        migrations.RemoveField(
            model_name='routepoint',
            name='route',
        ),
        migrations.DeleteModel(
            name='Layer',
        ),
        migrations.DeleteModel(
            name='Route',
        ),
        migrations.DeleteModel(
            name='RoutePoint',
        ),
    ]
