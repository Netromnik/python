# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0019_auto_20180704_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventtype',
            name='is_visible',
            field=models.BooleanField(default=True, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0432 \u0433\u043b\u0430\u0432\u043d\u043e\u043c \u043c\u0435\u043d\u044e'),
        ),
    ]
