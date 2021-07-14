# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-10 15:15
from __future__ import unicode_literals

from django.db import migrations
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0010_delete_bankproxy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='map',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, upload_to=b'img/site/phones/maps/', verbose_name='\u041a\u0430\u0440\u0442\u0430 \u043f\u0440\u043e\u0435\u0437\u0434\u0430'),
        ),
        migrations.AlterField(
            model_name='firms',
            name='logo',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, null=True, upload_to=b'img/site/phones/logo/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f'),
        ),
        migrations.AlterField(
            model_name='firms',
            name='map_logo',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 90x50 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', null=True, upload_to=b'img/site/phones/logo/map/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f \u043d\u0430 \u043a\u0430\u0440\u0442\u0435'),
        ),
        migrations.AlterField(
            model_name='firms',
            name='wide_image',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, null=True, upload_to=b'img/site/phones/wide/', verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='sections',
            name='logo',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, upload_to=b'img/site/phones/sections_logo/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f'),
        ),
        migrations.AlterField(
            model_name='sections',
            name='place_logo',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, null=True, upload_to=b'img/site/phones/place_logo/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f \u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0445 \u043c\u0435\u0441\u0442'),
        ),
    ]
