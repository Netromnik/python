# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0010_delete_adnews'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userratinghistory',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='establishment',
            name='total_editor_rating',
        ),
        migrations.RemoveField(
            model_name='establishment',
            name='total_user_rating',
        ),
        migrations.DeleteModel(
            name='UserRating',
        ),
        migrations.DeleteModel(
            name='UserRatingHistory',
        ),
    ]
