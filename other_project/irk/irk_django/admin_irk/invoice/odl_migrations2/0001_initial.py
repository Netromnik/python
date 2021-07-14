# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.invoice.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(default=irk.invoice.models.get_uuid, unique=True, max_length=64, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0437\u0430\u043a\u0430\u0437\u0430')),
                ('status', models.CharField(default='processed', max_length=16, verbose_name='\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442', choices=[('processed', '\u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435 \u043e\u043f\u043b\u0430\u0442\u044b'), ('cancel', '\u041e\u0442\u043c\u0435\u043d\u0435\u043d'), ('success', '\u0423\u0441\u043f\u0435\u0448\u043d\u043e'), ('fail', '\u041e\u0448\u0438\u0431\u043a\u0430')])),
                ('system', models.PositiveIntegerField(null=True, verbose_name='\u0421\u043f\u043e\u0441\u043e\u0431 \u043f\u043b\u0430\u0442\u0435\u0436\u0430', blank=True)),
                ('invoice', models.CharField(max_length=64, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u043e\u043f\u0435\u0440\u0430\u0442\u043e\u0440\u0430', blank=True)),
                ('amount', models.FloatField(verbose_name='\u0421\u0443\u043c\u043c\u0430 \u0437\u0430\u043a\u0430\u0437\u0430')),
                ('currency', models.CharField(default='RUB', choices=[('RUB', '\u0420\u0443\u0431\u043b\u0438'), ('USD', '\u0414\u043e\u043b\u043b\u0430\u0440\u044b \u0421\u0428\u0410'), ('EUR', '\u0415\u0432\u0440\u043e')], max_length=3, blank=True, null=True, verbose_name='\u0412\u0430\u043b\u044e\u0442\u0430')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0421\u043e\u0437\u0434\u0430\u043d')),
                ('performed_datetime', models.DateTimeField(null=True, verbose_name='\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d', blank=True)),
                ('company', models.CharField(default='moneta', max_length=16, verbose_name='\u041f\u043b\u0430\u0442\u0435\u0436\u043d\u0430\u044f \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u044f', choices=[('moneta', '\u041c\u043e\u043d\u0435\u0442\u0430.\u0440\u0443'), ('apple', ' App Store')])),
            ],
            options={
                'ordering': ('-created',),
                'verbose_name': '\u043f\u043b\u0430\u0442\u0435\u0436',
                'verbose_name_plural': '\u041f\u043b\u0430\u0442\u0435\u0436\u0438',
            },
        ),
    ]
