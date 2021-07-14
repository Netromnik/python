# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdWord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('caption', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430', blank=True)),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435', blank=True)),
                ('content_html', models.BooleanField(default=False, verbose_name='\u0412 \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0438 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f HTML')),
                ('url', models.URLField(verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u043e\u0432\u043e\u0441\u0442\u0438', blank=True)),
            ],
            options={
                'db_table': 'adwords_main',
                'verbose_name': '\u0440\u0435\u043a\u043b\u0430\u043c\u043d\u0430\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u044c',
                'verbose_name_plural': '\u0440\u0435\u043a\u043b\u0430\u043c\u043d\u044b\u0435 \u043d\u043e\u0432\u043e\u0441\u0442\u0438',
            },
        ),
        migrations.CreateModel(
            name='AdWordPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateField(verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('end', models.DateField(verbose_name='\u041a\u043e\u043d\u0435\u0446 \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
            ],
            options={
                'db_table': 'adwords_dates',
                'verbose_name': '\u043f\u0435\u0440\u0438\u043e\u0434',
                'verbose_name_plural': '\u043f\u0435\u0440\u0438\u043e\u0434\u044b',
            },
        ),
        migrations.CreateModel(
            name='CompanyNews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('caption', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430', blank=True)),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435', blank=True)),
                ('stamp', models.DateField(default=datetime.date.today, verbose_name='\u0414\u0430\u0442\u0430', db_index=True)),
                ('is_hidden', models.BooleanField(default=True, db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0442\u0430\u044f')),
                ('comments_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432', editable=False)),
            ],
            options={
                'verbose_name': '\u043d\u043e\u0432\u043e\u0441\u0442\u044c',
                'verbose_name_plural': '\u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0439',
            },
        ),
        migrations.CreateModel(
            name='CompanyNewsPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateField(verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('end', models.DateField(verbose_name='\u041a\u043e\u043d\u0435\u0446 \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('news', models.ForeignKey(related_name='period', to='adwords.CompanyNews')),
            ],
            options={
                'verbose_name': '\u043f\u0435\u0440\u0438\u043e\u0434',
                'verbose_name_plural': '\u043f\u0435\u0440\u0438\u043e\u0434\u044b',
            },
        ),
    ]
