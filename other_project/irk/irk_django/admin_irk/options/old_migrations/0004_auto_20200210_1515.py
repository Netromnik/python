# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-10 15:15
from __future__ import unicode_literals

from django.db import migrations
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0003_auto_20200122_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='branding_image',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, help_text='\u0420\u0430\u0437\u043c\u0435\u0440\u044b \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f: 1920\xd7250 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', null=True, upload_to=b'img/site/adv/branding', verbose_name='\u0411\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='site',
            name='icon',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, null=True, upload_to=b'img/site/option/icon/', verbose_name='\u0418\u043a\u043e\u043d\u043a\u0430'),
        ),
        migrations.AlterField(
            model_name='site',
            name='widget_image',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, help_text='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f \u0441\u043f\u0440\u0430\u0432\u0430 \u043e\u0442 \u043c\u0435\u043d\u044e', null=True, upload_to=b'img/site/adv/widgets', verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0432\u0438\u0434\u0436\u0435\u0442\u0430'),
        ),
    ]