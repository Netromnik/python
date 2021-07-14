# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.db.models.fields.color
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Logo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u043c\u0435\u0440: 200x74 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/logo', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f')),
                ('color', irk.utils.db.models.fields.color.ColorField(help_text='\u0412 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 #13bf99', max_length=6, null=True, verbose_name='\u0426\u0432\u0435\u0442', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('start_month', models.IntegerField(default=0, verbose_name='\u041c\u0435\u0441\u044f\u0446 \u043d\u0430\u0447\u0430\u043b\u0430 \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('start_day', models.IntegerField(default=0, verbose_name='\u0414\u0435\u043d\u044c \u043d\u0430\u0447\u0430\u043b\u0430 \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('end_month', models.IntegerField(default=0, verbose_name='\u041c\u0435\u0441\u044f\u0446 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('end_day', models.IntegerField(default=0, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('create_stamp', models.DateField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('visible', models.BooleanField(default=True, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043d\u0430 \u0441\u0430\u0439\u0442\u0435')),
            ],
            options={
                'verbose_name': '\u043b\u043e\u0433\u043e\u0442\u0438\u043f',
                'verbose_name_plural': '\u043b\u043e\u0433\u043e\u0442\u0438\u043f\u044b',
            },
        ),
    ]
