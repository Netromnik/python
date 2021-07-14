# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magazine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='magazine',
            name='caption',
            field=models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430', blank=True),
        ),
        migrations.AlterField(
            model_name='magazine',
            name='home_image',
            field=models.ImageField(upload_to=b'img/site/magazine/', null=True, verbose_name='\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0434\u043b\u044f \u0433\u043b\u0430\u0432\u043d\u043e\u0439', blank=True),
        ),
        migrations.AlterField(
            model_name='magazinesubscriber',
            name='hash',
            field=models.CharField(max_length=40, editable=False, db_index=True),
        ),
    ]
