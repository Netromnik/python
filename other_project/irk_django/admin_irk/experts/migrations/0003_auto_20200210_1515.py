# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-10 15:15
from __future__ import unicode_literals

from django.db import migrations
import irk.experts.models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0002_auto_20161212_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expert',
            name='avatar',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, help_text='\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0432 \u043e\u0442\u0432\u0435\u0442\u0430\u0445 \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u0430.<br />\u0424\u043e\u0442\u043e \u0434\u043e\u043b\u0436\u043d\u043e \u0431\u044b\u0442\u044c \u043a\u0432\u0430\u0434\u0440\u0430\u0442\u043d\u044b\u043c! \u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u043c\u0435\u0440 200x200.', null=True, upload_to=b'img/site/experts/avatars/', verbose_name='\u0410\u0432\u0430\u0442\u0430\u0440\u043a\u0430'),
        ),
        migrations.AlterField(
            model_name='expert',
            name='image',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, help_text='\u041e\u043f\u0442\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u043c\u0435\u0440 \u0444\u043e\u0442\u043e 705\u0445470, \u043c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 460\u0445307. \u041f\u0440\u043e\u043f\u043e\u0440\u0446\u0438\u044f 3:2.', null=True, upload_to=b'img/site/experts/', verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='expert',
            name='picture',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, null=True, upload_to=b'img/site/experts/', verbose_name='\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430'),
        ),
        migrations.AlterField(
            model_name='expert',
            name='wide_image',
            field=irk.utils.fields.file.ImageRemovableField(blank=True, help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', null=True, upload_to=irk.experts.models.expert_image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f'),
        ),
    ]