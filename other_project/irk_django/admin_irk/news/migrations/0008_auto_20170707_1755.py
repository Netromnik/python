# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_auto_20170627_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basematerial',
            name='magazine_image',
            field=models.ImageField(upload_to=b'img/site/news/magazine', null=True, verbose_name='\u0424\u043e\u0442\u043e \u0434\u043b\u044f \u0436\u0443\u0440\u043d\u0430\u043b\u0430', blank=True),
        ),
    ]
