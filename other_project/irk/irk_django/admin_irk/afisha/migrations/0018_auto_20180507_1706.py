# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0017_auto_20171116_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='show_comments',
        ),
        migrations.AlterField(
            model_name='event',
            name='disable_comments',
            field=models.BooleanField(default=False, help_text='\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u0432\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f', db_index=True, verbose_name='\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='event',
            name='hide_comments',
            field=models.BooleanField(default=False, help_text='\u043e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u044b \u0431\u0435\u0437 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043f\u0440\u043e 24 \u0447\u0430\u0441\u0430', db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438'),
        ),
        migrations.AlterField(
            model_name='eventguide',
            name='source',
            field=models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name='\u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a', choices=[(0, b'\xd0\x92\xd1\x80\xd1\x83\xd1\x87\xd0\xbd\xd1\x83\xd1\x8e'), (1, b'\xd0\xa0\xd0\xb0\xd0\xbc\xd0\xb1\xd0\xbb\xd0\xb5\xd1\x80'), (2, b'\xd0\x9a\xd0\xb8\xd0\xbd\xd0\xbe\xd0\xbc\xd0\xb0\xd0\xba\xd1\x81')]),
        ),
    ]
