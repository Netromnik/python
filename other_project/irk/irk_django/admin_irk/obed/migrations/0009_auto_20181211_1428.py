# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0008_auto_20181029_1621'),
    ]

    operations = [
        migrations.DeleteModel(
            name='District',
        ),
        migrations.RemoveField(
            model_name='menuofday',
            name='establishment',
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
        migrations.RemoveField(
            model_name='promotion',
            name='establishment',
        ),
        migrations.RemoveField(
            model_name='tastystory',
            name='firm',
        ),
        migrations.AlterUniqueTogether(
            name='userrate',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='userrate',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='userrate',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userratehistory',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='userratehistory',
            name='user',
        ),
        migrations.DeleteModel(
            name='MenuOfDay',
        ),
        migrations.DeleteModel(
            name='Promotion',
        ),
        migrations.DeleteModel(
            name='TastyStory',
        ),
        migrations.DeleteModel(
            name='UserRate',
        ),
        migrations.DeleteModel(
            name='UserRateHistory',
        ),
    ]
