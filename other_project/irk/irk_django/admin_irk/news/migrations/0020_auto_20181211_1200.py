# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0019_20180925_socpult_scheduler'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CoinRate',
        ),
        migrations.DeleteModel(
            name='Press',
        ),
        migrations.DeleteModel(
            name='Words',
        ),
    ]
