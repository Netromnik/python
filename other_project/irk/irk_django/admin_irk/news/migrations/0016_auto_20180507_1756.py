# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0015_remove_basematerial_show_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basematerial',
            name='comment_disable_stamp',
        ),
        # migrations.RemoveField(
        #     model_name='basematerial',
        #     name='last_comment',
        # ),
        # migrations.RemoveField(
        #     model_name='flash',
        #     name='last_comment',
        # ),
    ]
