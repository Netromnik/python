# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0002_auto_20161212_1624'),
        ('tourism', '0003_auto_20181211_1145'),
        ('phones', '0010_delete_bankproxy'),
        ('currency', '0002_auto_20161212_1624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bank',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='credit',
            name='bank',
        ),
        migrations.RemoveField(
            model_name='currencyrate',
            name='bank',
        ),
        migrations.RemoveField(
            model_name='currencyratelog',
            name='bank',
        ),
        migrations.RemoveField(
            model_name='currencyratelog',
            name='user',
        ),
        migrations.RemoveField(
            model_name='deposit',
            name='bank',
        ),
        migrations.DeleteModel(
            name='News',
        ),
        migrations.DeleteModel(
            name='Bank',
        ),
        migrations.DeleteModel(
            name='Credit',
        ),
        migrations.DeleteModel(
            name='CurrencyRate',
        ),
        migrations.DeleteModel(
            name='CurrencyRateLog',
        ),
        migrations.DeleteModel(
            name='Deposit',
        ),
    ]
