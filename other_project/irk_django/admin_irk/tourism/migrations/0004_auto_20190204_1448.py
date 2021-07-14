# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0003_auto_20181211_1145'),
    ]

    operations = [
        #migrations.RemoveField(
            #model_name='order',
            #name='tour_firms',
        #),
        #migrations.RemoveField(
            #model_name='tourfirm',
            #name='tour_order',
        #),
        migrations.DeleteModel(
            name='Order',
        ),
    ]
