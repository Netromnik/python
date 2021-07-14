# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='position',
            field=models.IntegerField(verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', db_index=True),
        ),
    ]
