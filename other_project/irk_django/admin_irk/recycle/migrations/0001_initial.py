# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-06-14 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=120, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438')),
                ('name_html', models.CharField(blank=True, default='', max_length=120, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 (html)')),
                ('image', models.ImageField(blank=True, upload_to='photo', verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('icon_class', models.CharField(default='', max_length=100, verbose_name='\u041a\u043b\u0430\u0441\u0441 \u0438\u043a\u043e\u043d\u043a\u0438')),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': '\u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u043e\u0442\u0445\u043e\u0434\u043e\u0432',
                'verbose_name_plural': '\u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 \u043e\u0442\u0445\u043e\u0434\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='Dot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=512, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0443\u043d\u043a\u0442\u0430')),
                ('description', models.TextField(default='', verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('addres', models.CharField(default='', max_length=512, verbose_name='\u0410\u0434\u0440\u0435\u0441')),
                ('phone', models.TextField(default='', verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d')),
                ('x', models.FloatField(verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430 \u0445')),
                ('y', models.FloatField(verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430 \u0443')),
                ('working_hours', models.TextField(default='', verbose_name='\u0412\u0440\u0435\u043c\u044f \u0438 \u0447\u0430\u0441\u044b \u0440\u0430\u0431\u043e\u0442\u044b')),
                ('image', models.ImageField(blank=True, upload_to='photo_garbage', verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('categories', models.ManyToManyField(to='recycle.Category', verbose_name='\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u043c\u0443\u0441\u043e\u0440\u0430')),
            ],
            options={
                'verbose_name': '\u043f\u0443\u043d\u043a\u0442 \u043f\u0435\u0440\u0435\u0440\u0430\u0431\u043e\u0442\u043a\u0438',
                'verbose_name_plural': '\u043f\u0443\u043d\u043a\u0442\u044b \u043f\u0435\u0440\u0435\u0440\u0430\u0431\u043e\u0442\u043a\u0438',
            },
        ),
    ]
