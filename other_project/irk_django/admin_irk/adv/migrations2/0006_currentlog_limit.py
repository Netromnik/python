# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0005_place_targetix2_moevideo'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, '\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440'), (2, '\u041f\u0435\u0440\u0435\u0445\u043e\u0434'), (3, '\u0414\u043e\u0441\u043a\u0440\u043e\u043b\u043b')])),
                ('stamp', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f')),
                ('cnt', models.PositiveIntegerField()),
                ('banner', models.ForeignKey(verbose_name='\u0411\u0430\u043d\u043d\u0435\u0440', to='adv.Banner')),
                ('file', models.ForeignKey(to='adv.File', null=True)),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043f\u0438\u0441\u044c',
                'verbose_name_plural': '\u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430',
            },
        ),
        migrations.CreateModel(
            name='Limit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0432\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f', null=True, editable=False)),
                ('auto_disabled', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0432\u044b\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f', null=True, editable=False)),
                ('updated', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0438', null=True, editable=False)),
                ('view_limit', models.IntegerField(default=0, verbose_name='\u041e\u0433\u0440\u0430\u043d\u0447\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432')),
                ('view_left', models.IntegerField(default=0, verbose_name='\u041f\u0440\u043e\u0441\u043c\u0442\u043e\u0440\u043e\u0432 \u043e\u0441\u0442\u0430\u043b\u043e\u0441\u044c')),
                ('is_active', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u043a\u043b\u044e\u0447\u0435\u043d')),
                ('banner', models.OneToOneField(to='adv.Banner')),
            ],
            options={
                'verbose_name': '\u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435 \u043d\u0430 \u043f\u043e\u043a\u0430\u0437\u044b',
                'verbose_name_plural': '\u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u044f \u043d\u0430 \u043f\u043e\u043a\u0430\u0437\u044b',
            },
        ),
    ]
