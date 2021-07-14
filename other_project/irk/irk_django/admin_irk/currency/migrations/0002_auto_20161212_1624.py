# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0002_auto_20161212_1624'),
        ('phones', '0002_bankproxy'),
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
            ],
            options={
                'verbose_name': '\u043d\u043e\u0432\u043e\u0441\u0442\u044c',
                'proxy': True,
                'verbose_name_plural': '\u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('news.news',),
        ),
        migrations.AddField(
            model_name='deposit',
            name='bank',
            field=models.ForeignKey(verbose_name='\u0411\u0430\u043d\u043a', to='phones.Firms'),
        ),
        migrations.AddField(
            model_name='currencyratelog',
            name='bank',
            field=models.ForeignKey(to='currency.Bank'),
        ),
        migrations.AddField(
            model_name='currencyratelog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='currencyrate',
            name='bank',
            field=models.ForeignKey(to='currency.Bank', db_column=b'bank'),
        ),
        migrations.AddField(
            model_name='credit',
            name='bank',
            field=models.ForeignKey(verbose_name='\u0411\u0430\u043d\u043a', to='currency.Bank'),
        ),
        migrations.AddField(
            model_name='bank',
            name='parent',
            field=models.ForeignKey(related_name='bank_branches', verbose_name='\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043e\u0442\u0434\u0435\u043b\u0435\u043d\u0438\u0435', blank=True, to='currency.Bank', null=True),
        ),
    ]
