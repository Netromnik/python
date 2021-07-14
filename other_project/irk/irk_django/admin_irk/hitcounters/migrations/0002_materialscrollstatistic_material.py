# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hitcounters', '0001_initial'),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialscrollstatistic',
            name='material',
            field=models.OneToOneField(related_name='scroll_statistic', verbose_name='\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b', to='news.BaseMaterial'),
        ),
    ]
