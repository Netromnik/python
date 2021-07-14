# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='content',
            field=models.TextField(default='', blank=True, verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435'),
        ),
        migrations.RenameField(
            model_name='quiz',
            old_name='title',
            new_name='name',
        ),
        migrations.AddField(
            model_name='quiz',
            name='title',
            field=models.CharField(default='', max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435'),
        ),

    ]
