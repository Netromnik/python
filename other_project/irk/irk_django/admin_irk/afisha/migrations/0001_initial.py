# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('place', models.PositiveSmallIntegerField(choices=[(1, '\u0421\u043b\u0430\u0439\u0434\u0435\u0440 \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439 \u0410\u0444\u0438\u0448\u0438'), (2, '\u0421\u043b\u0430\u0439\u0434\u0435\u0440 \u043f\u043e\u0434\u0440\u0430\u0437\u0434\u0435\u043b\u043e\u0432 \u0410\u0444\u0438\u0448\u0438'), (3, '\u0421\u043b\u0430\u0439\u0434\u0435\u0440 \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')], blank=True, help_text='\u0415\u0441\u043b\u0438 \u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u043e, \u0430\u043d\u043e\u043d\u0441 \u0432\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f \u0432\u0435\u0437\u0434\u0435', null=True, verbose_name='\u043c\u0435\u0441\u0442\u043e', db_index=True)),
                ('start', models.DateField(verbose_name='\u043d\u0430\u0447\u0430\u043b\u043e', db_index=True)),
                ('end', models.DateField(verbose_name='\u043a\u043e\u043d\u0435\u0446', db_index=True)),
            ],
            options={
                'verbose_name': '\u0430\u043d\u043e\u043d\u0441',
                'verbose_name_plural': '\u0430\u043d\u043e\u043d\u0441\u044b',
            },
        ),
        migrations.CreateModel(
            name='AnnouncementColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=6, verbose_name='\u0426\u0432\u0435\u0442')),
                ('position', models.SmallIntegerField(verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', blank=True)),
            ],
            options={
                'verbose_name': '\u0446\u0432\u0435\u0442',
                'verbose_name_plural': '\u0446\u0432\u0435\u0442\u0430',
            },
        ),
    ]
