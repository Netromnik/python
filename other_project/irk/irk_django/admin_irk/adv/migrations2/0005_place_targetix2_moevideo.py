# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0004_auto_20180329_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='targetix2',
            field=models.ForeignKey(related_name='places2', blank=True, to='adv.Targetix', help_text='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f 50/50 \u0441 \u0432\u043d\u0435\u0448\u043d\u0438\u043c \u0431\u0430\u043d\u043d\u0435\u0440\u043e\u043c 1', null=True, verbose_name='\u0412\u043d\u0435\u0448\u043d\u0438\u0439 \u0431\u0430\u043d\u043d\u0435\u0440 2'),
        ),
        migrations.AlterField(
            model_name='place',
            name='targetix',
            field=models.ForeignKey(related_name='places', verbose_name='\u0412\u043d\u0435\u0448\u043d\u0438\u0439 \u0431\u0430\u043d\u043d\u0435\u0440', blank=True, to='adv.Targetix', null=True),
        ),
    ]
