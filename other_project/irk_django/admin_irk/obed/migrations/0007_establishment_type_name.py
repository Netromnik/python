# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0006_auto_20181011_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='establishment',
            name='type_name',
            field=models.CharField(default=b'', help_text='\u041f\u0440\u0438\u043c\u0435\u0440: \u0420\u0435\u0441\u0442\u043e\u0440\u0430\u043d', max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0442\u0438\u043f\u0430 \u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f', blank=True),
        ),
    ]
