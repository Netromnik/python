# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0009_auto_20181211_1428'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AdNews',
        ),
    ]
