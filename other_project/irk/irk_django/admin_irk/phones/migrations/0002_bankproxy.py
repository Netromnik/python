# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0001_initial'),
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankProxy',
            fields=[
            ],
            options={
                'verbose_name': '\u0411\u0430\u043d\u043a',
                'proxy': True,
                'verbose_name_plural': '\u0411\u0430\u043d\u043a\u0438',
            },
            bases=('currency.bank',),
        ),
    ]
