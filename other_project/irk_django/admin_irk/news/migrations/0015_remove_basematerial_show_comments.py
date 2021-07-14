# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0014_scheduledtask_helptexts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basematerial',
            name='show_comments',
        ),
    ]
