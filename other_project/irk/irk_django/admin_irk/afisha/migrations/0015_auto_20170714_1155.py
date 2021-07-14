# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0014_auto_20170621_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventguide',
            name='source',
            field=models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='\u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a', choices=[(0, b'\xd0\x92 \xd1\x80\xd1\x83\xd1\x87\xd0\xbd\xd1\x83\xd1\x8e'), (1, b'\xd0\xa0\xd0\xb0\xd0\xbc\xd0\xb1\xd0\xbb\xd0\xb5\xd1\x80'), (2, b'\xd0\x9a\xd0\xb8\xd0\xbd\xd0\xbe\xd0\xbc\xd0\xb0\xd0\xba\xd1\x81')]),
        ),
    ]
