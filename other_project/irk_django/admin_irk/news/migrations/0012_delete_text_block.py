# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0011_auto_20170901_1437'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TextBlock',
        ),
    ]
