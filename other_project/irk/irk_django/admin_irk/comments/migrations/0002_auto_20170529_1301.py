# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(
                verbose_name='\u0434\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f',
                auto_now=True, db_index=True
            ),
        ),
        migrations.AlterField(
            model_name='comment',
            name='modified',
            field=models.DateTimeField(
                verbose_name='\u0434\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f',
                auto_now_add=True, db_index=True
            ),
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(related_name='answers', blank=True, to='comments.Comment', null=True),
        ),
    ]
