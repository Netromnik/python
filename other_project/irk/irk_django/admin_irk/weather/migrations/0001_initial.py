# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FirePlace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('center', django.contrib.gis.db.models.fields.PointField(srid=4326, spatial_index=False, verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b')),
                ('created', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f')),
            ],
            options={
                'db_table': 'weather_fireplaces',
                'verbose_name': '\u043b\u0435\u0441\u043d\u043e\u0439 \u043f\u043e\u0436\u0430\u0440',
                'verbose_name_plural': '\u043b\u0435\u0441\u043d\u044b\u0435 \u043f\u043e\u0436\u0430\u0440\u044b',
            },
        ),
        migrations.CreateModel(
            name='Joke',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.PositiveSmallIntegerField(db_index=True, verbose_name='\u043c\u0435\u0441\u044f\u0446', choices=[(1, '\u044f\u043d\u0432\u0430\u0440\u044c'), (2, '\u0444\u0435\u0432\u0440\u0430\u043b\u044c'), (3, '\u043c\u0430\u0440\u0442'), (4, '\u0430\u043f\u0440\u0435\u043b\u044c'), (5, '\u043c\u0430\u0439'), (6, '\u0438\u044e\u043d\u044c'), (7, '\u0438\u044e\u043b\u044c'), (8, '\u0430\u0432\u0433\u0443\u0441\u0442'), (9, '\u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044c'), (10, '\u043e\u043a\u0442\u044f\u0431\u0440\u044c'), (11, '\u043d\u043e\u044f\u0431\u0440\u044c'), (12, '\u0434\u0435\u043a\u0430\u0431\u0440\u044c')])),
                ('day', models.PositiveSmallIntegerField(verbose_name='\u0434\u0435\u043d\u044c', db_index=True)),
                ('content', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442')),
            ],
            options={
                'verbose_name': '\u0430\u043d\u0435\u043a\u0434\u043e\u0442',
                'verbose_name_plural': '\u0430\u043d\u0435\u043a\u0434\u043e\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='MeteoCentre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stamp', models.DateField(unique=True, verbose_name='\u0414\u0430\u0442\u0430')),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('storm_caption', models.CharField(max_length=20, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0448\u0442\u043e\u0440\u043c\u043e\u0432\u043e\u0433\u043e', blank=True)),
                ('storm_content', models.TextField(max_length=125, verbose_name='\u0428\u0442\u043e\u0440\u043c\u043e\u0432\u043e\u0435', blank=True)),
            ],
            options={
                'db_table': 'weather_meteocentre',
                'verbose_name': '\u043f\u0440\u043e\u0433\u043d\u043e\u0437 \u0433\u0438\u0434\u0440\u043e\u043c\u0435\u0442\u0435\u043e\u0446\u0435\u043d\u0442\u0440\u0430',
                'verbose_name_plural': '\u043f\u0440\u043e\u0433\u043d\u043e\u0437 \u0433\u0438\u0434\u0440\u043e\u043c\u0435\u0442\u0435\u043e\u0446\u0435\u043d\u0442\u0440\u0430',
            },
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('alias', models.CharField(max_length=15, verbose_name='\u0430\u043b\u0438\u0430\u0441', db_index=True)),
                ('number', models.PositiveSmallIntegerField(help_text='\u041e\u0442\u0441\u0447\u0435\u0442 \u0441 \u043d\u0443\u043b\u044f', verbose_name='\u043f\u043e\u0440\u044f\u0434\u043a\u043e\u0432\u044b\u0439 \u043d\u043e\u043c\u0435\u0440', db_index=True)),
            ],
            options={
                'ordering': ['number'],
                'verbose_name': '\u041c\u0435\u0441\u044f\u0446',
                'verbose_name_plural': '\u041c\u0435\u0441\u044f\u0446\u0430',
            },
        ),
        migrations.CreateModel(
            name='MoonDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.PositiveSmallIntegerField(unique=True, verbose_name='\u043d\u043e\u043c\u0435\u0440')),
                ('title', models.CharField(max_length=50, verbose_name='\u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True)),
                ('symbol', models.CharField(max_length=50, verbose_name='\u0441\u0438\u043c\u0432\u043e\u043b', blank=True)),
                ('stones', models.CharField(max_length=100, verbose_name='\u043a\u0430\u043c\u043d\u0438', blank=True)),
                ('content', models.TextField(verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('for_undertaking', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u043d\u0430\u0447\u0438\u043d\u0430\u043d\u0438\u044f', choices=[(1, '\u0443\u0436\u0430\u0441\u043d\u043e'), (2, '\u043f\u043b\u043e\u0445\u043e'), (3, '\u043d\u043e\u0440\u043c\u0430'), (4, '\u0445\u043e\u0440\u043e\u0448\u043e'), (5, '\u043e\u0442\u043b\u0438\u0447\u043d\u043e')])),
                ('for_money', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u0434\u0435\u043d\u044c\u0433\u0438', choices=[(1, '\u0443\u0436\u0430\u0441\u043d\u043e'), (2, '\u043f\u043b\u043e\u0445\u043e'), (3, '\u043d\u043e\u0440\u043c\u0430'), (4, '\u0445\u043e\u0440\u043e\u0448\u043e'), (5, '\u043e\u0442\u043b\u0438\u0447\u043d\u043e')])),
                ('for_dream', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u0441\u043d\u044b', choices=[(1, '\u0443\u0436\u0430\u0441\u043d\u043e'), (2, '\u043f\u043b\u043e\u0445\u043e'), (3, '\u043d\u043e\u0440\u043c\u0430'), (4, '\u0445\u043e\u0440\u043e\u0448\u043e'), (5, '\u043e\u0442\u043b\u0438\u0447\u043d\u043e')])),
                ('for_housework', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u0434\u043e\u043c\u0430\u0448\u043d\u0438\u0435 \u0434\u0435\u043b\u0430', choices=[(1, '\u0443\u0436\u0430\u0441\u043d\u043e'), (2, '\u043f\u043b\u043e\u0445\u043e'), (3, '\u043d\u043e\u0440\u043c\u0430'), (4, '\u0445\u043e\u0440\u043e\u0448\u043e'), (5, '\u043e\u0442\u043b\u0438\u0447\u043d\u043e')])),
                ('for_haircut', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u0441\u0442\u0440\u0438\u0436\u043a\u0430', choices=[(1, '\u0443\u0436\u0430\u0441\u043d\u043e'), (2, '\u043f\u043b\u043e\u0445\u043e'), (3, '\u043d\u043e\u0440\u043c\u0430'), (4, '\u0445\u043e\u0440\u043e\u0448\u043e'), (5, '\u043e\u0442\u043b\u0438\u0447\u043d\u043e')])),
                ('for_drink', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u0437\u0430\u0441\u0442\u043e\u043b\u044c\u0435', choices=[(1, '\u0443\u0436\u0430\u0441\u043d\u043e'), (2, '\u043f\u043b\u043e\u0445\u043e'), (3, '\u043d\u043e\u0440\u043c\u0430'), (4, '\u0445\u043e\u0440\u043e\u0448\u043e'), (5, '\u043e\u0442\u043b\u0438\u0447\u043d\u043e')])),
            ],
            options={
                'ordering': ['number'],
                'verbose_name': '\u043b\u0443\u043d\u043d\u044b\u0439 \u0434\u0435\u043d\u044c',
                'verbose_name_plural': '\u043b\u0443\u043d\u043d\u044b\u0435 \u0434\u043d\u0438',
            },
        ),
        migrations.CreateModel(
            name='MoonTiming',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(verbose_name='\u043d\u0430\u0447\u0430\u043b\u043e', db_index=True)),
                ('end_date', models.DateTimeField(verbose_name='\u043a\u043e\u043d\u0435\u0446', db_index=True)),
                ('number', models.PositiveSmallIntegerField(verbose_name='\u043d\u043e\u043c\u0435\u0440')),
            ],
            options={
                'ordering': ['start_date'],
                'verbose_name': '\u0437\u0430\u043f\u0438\u0441\u044c \u043b\u0443\u043d\u043d\u043e\u0433\u043e \u0433\u0440\u0430\u0444\u0438\u043a\u0430',
                'verbose_name_plural': '\u043b\u0443\u043d\u043d\u044b\u0439 \u0433\u0440\u0430\u0444\u0438\u043a',
            },
        ),
        migrations.CreateModel(
            name='WeatherCities',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0434\u0430\u0442\u0430')),
                ('day', models.IntegerField(null=True, verbose_name='\u0434\u043d\u0435\u0432\u043d\u0430\u044f', blank=True)),
                ('night', models.IntegerField(null=True, verbose_name='\u043d\u043e\u0447\u043d\u0430\u044f', blank=True)),
                ('wind', models.IntegerField(null=True, verbose_name='\u0441\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u0432\u0435\u0442\u0440\u0430', blank=True)),
                ('wind_t', models.IntegerField(null=True, verbose_name='\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0432\u0435\u0442\u0440\u0430', blank=True)),
                ('nebulosity', models.IntegerField(null=True, verbose_name='\u043e\u0431\u043b\u0430\u0447\u043d\u043e\u0441\u0442\u044c', blank=True)),
                ('precipitation', models.IntegerField(null=True, verbose_name='\u043e\u0441\u0430\u0434\u043a\u0438', blank=True)),
                ('sun_v', models.TimeField(null=True, verbose_name='\u0432\u043e\u0441\u0445\u043e\u0434', blank=True)),
                ('sun_z', models.TimeField(null=True, verbose_name='\u0437\u0430\u0445\u043e\u0434', blank=True)),
                ('stamp', models.DateTimeField(null=True, verbose_name='\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u0430\u044f \u043c\u0435\u0442\u043a\u0430')),
                ('source', models.IntegerField(verbose_name='\u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a \u0434\u0430\u043d\u043d\u044b\u0445')),
                ('city', models.ForeignKey(db_column=b'city', verbose_name='\u0433\u043e\u0440\u043e\u0434', to='map.Cities')),
            ],
            options={
                'db_table': 'weather_cities',
            },
        ),
        migrations.CreateModel(
            name='WeatherDetailed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(verbose_name='\u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f')),
                ('day', models.PositiveIntegerField(verbose_name='\u0447\u0438\u0441\u043b\u043e', db_index=True)),
                ('hour', models.PositiveIntegerField(verbose_name='\u0447\u0430\u0441')),
                ('wind', models.IntegerField(null=True, verbose_name='\u0441\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u0432\u0435\u0442\u0440\u0430', blank=True)),
                ('wind_t', models.IntegerField(null=True, verbose_name='\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0432\u0435\u0442\u0440\u0430', blank=True)),
                ('temp_from', models.IntegerField(null=True, verbose_name='\u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u043e\u0442', blank=True)),
                ('temp_to', models.IntegerField(null=True, verbose_name='\u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u0434\u043e', blank=True)),
                ('temp_feel', models.IntegerField(null=True, verbose_name='\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u043f\u043e \u043e\u0449\u0443\u0449\u0435\u043d\u0438\u044f\u043c', blank=True)),
                ('mm', models.PositiveIntegerField(null=True, verbose_name='\u0434\u0430\u0432\u043b\u0435\u043d\u0438\u0435', blank=True)),
                ('humidity', models.PositiveIntegerField(null=True, verbose_name='\u0432\u043b\u0430\u0436\u043d\u043e\u0441\u0442\u044c', blank=True)),
                ('nebulosity', models.IntegerField(null=True, verbose_name='\u043e\u0431\u043b\u0430\u0447\u043d\u043e\u0441\u0442\u044c', blank=True)),
                ('precipitation', models.IntegerField(null=True, verbose_name='\u043e\u0441\u0430\u0434\u043a\u0438', blank=True)),
                ('city', models.ForeignKey(verbose_name='\u0433\u043e\u0440\u043e\u0434', to='map.Cities')),
            ],
            options={
                'db_table': 'weather_detailed',
            },
        ),
        migrations.CreateModel(
            name='WeatherFact',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('datetime', models.DateTimeField(verbose_name='\u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f')),
                ('day', models.IntegerField(help_text='\u0412 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 %m%d', verbose_name='\u0434\u0435\u043d\u044c')),
                ('temp', models.IntegerField(null=True, verbose_name='\u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430', blank=True)),
                ('temp_feel', models.IntegerField(null=True, verbose_name='\u0422\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430 \u043f\u043e \u043e\u0449\u0443\u0449\u0435\u043d\u0438\u044f\u043c', blank=True)),
                ('weather_code', models.IntegerField(null=True, verbose_name='\u043a\u043e\u0434 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u044f \u043f\u043e\u0433\u043e\u0434\u044b', blank=True)),
                ('nebulosity', models.IntegerField(null=True, verbose_name='\u043e\u0431\u043b\u0430\u0447\u043d\u043e\u0441\u0442\u044c', blank=True)),
                ('mm', models.IntegerField(null=True, verbose_name='\u0434\u0430\u0432\u043b\u0435\u043d\u0438\u0435', blank=True)),
                ('wind', models.IntegerField(null=True, verbose_name='\u0441\u043a\u043e\u0440\u043e\u0441\u0442\u044c \u0432\u0435\u0442\u0440\u0430', blank=True)),
                ('wind_t', models.IntegerField(null=True, verbose_name='\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0432\u0435\u0442\u0440\u0430', blank=True)),
                ('humidity', models.IntegerField(null=True, verbose_name='\u0432\u043b\u0430\u0436\u043d\u043e\u0441\u0442\u044c', blank=True)),
                ('visibility', models.PositiveIntegerField(null=True, verbose_name='\u0412\u0438\u0434\u0438\u043c\u043e\u0441\u0442\u044c, \u043c.', blank=True)),
                ('city', models.IntegerField(null=True, verbose_name='\u0433\u043e\u0440\u043e\u0434', blank=True)),
            ],
            options={
                'db_table': 'weather_fact',
            },
        ),
        migrations.CreateModel(
            name='WeatherGm',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0434\u0430\u0442\u0430')),
                ('hour', models.IntegerField(verbose_name='\u0447\u0430\u0441')),
                ('status', models.IntegerField(verbose_name='\u0447\u0438\u0441\u043b\u043e\u0432\u043e\u0439 \u043a\u043e\u0434')),
            ],
            options={
                'db_table': 'weather_gm',
            },
        ),
        migrations.CreateModel(
            name='WeatherSigns',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.IntegerField(verbose_name='\u041c\u0435\u0441\u044f\u0446', choices=[(1, '\u044f\u043d\u0432\u0430\u0440\u044c'), (2, '\u0444\u0435\u0432\u0440\u0430\u043b\u044c'), (3, '\u043c\u0430\u0440\u0442'), (4, '\u0430\u043f\u0440\u0435\u043b\u044c'), (5, '\u043c\u0430\u0439'), (6, '\u0438\u044e\u043d\u044c'), (7, '\u0438\u044e\u043b\u044c'), (8, '\u0430\u0432\u0433\u0443\u0441\u0442'), (9, '\u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044c'), (10, '\u043e\u043a\u0442\u044f\u0431\u0440\u044c'), (11, '\u043d\u043e\u044f\u0431\u0440\u044c'), (12, '\u0434\u0435\u043a\u0430\u0431\u0440\u044c')])),
                ('day', models.IntegerField(verbose_name='\u0414\u0435\u043d\u044c')),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
            ],
            options={
                'db_table': 'weather_signs',
                'verbose_name': '\u043f\u0440\u0438\u043c\u0435\u0442\u0443',
                'verbose_name_plural': '\u043f\u0440\u0438\u043c\u0435\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='WeatherTemp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stamp', models.DateField(unique=True)),
                ('hour', models.IntegerField(unique=True)),
                ('place', models.IntegerField(unique=True)),
                ('temp', models.IntegerField(null=True, blank=True)),
                ('city', models.IntegerField()),
            ],
            options={
                'db_table': 'weather_temp',
            },
        ),
        migrations.CreateModel(
            name='WeatherTempHour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('temp', models.IntegerField(verbose_name='\u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430')),
                ('time', models.DateTimeField(verbose_name='\u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f')),
                ('place', models.IntegerField(verbose_name='\u043c\u0435\u0441\u0442\u043e')),
                ('city', models.IntegerField(verbose_name='\u0433\u043e\u0440\u043e\u0434')),
                ('mm', models.IntegerField(null=True, verbose_name='\u0434\u0430\u0432\u043b\u0435\u043d\u0438\u0435', blank=True)),
            ],
            options={
                'db_table': 'weather_temp_hour',
            },
        ),
        migrations.CreateModel(
            name='WishForConditions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 1920x440', upload_to=b'img/site/weather/wishes/', verbose_name='\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('text', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442')),
                ('t_min', models.IntegerField(null=True, verbose_name='\u043c\u0438\u043d \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430', blank=True)),
                ('t_max', models.IntegerField(null=True, verbose_name='\u043c\u0430\u043a\u0441 \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0430', blank=True)),
                ('is_storm', models.BooleanField(default=False, db_index=True, verbose_name='\u0448\u0442\u043e\u0440\u043c\u043e\u0432\u043e\u0435')),
                ('is_strong_wind', models.BooleanField(default=False, help_text='\u0411\u043e\u043b\u044c\u0448\u0435 15 \u043c/\u0441 (\u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435\u043b\u044c\u043d\u043e)', db_index=True, verbose_name='\u0441\u0438\u043b\u044c\u043d\u044b\u0439 \u0432\u0435\u0442\u0435\u0440')),
                ('is_cloudy', models.BooleanField(default=False, db_index=True, verbose_name='\u043e\u0431\u043b\u0430\u0447\u043d\u043e \u0438\u043b\u0438 \u043f\u0430\u0441\u043c\u0443\u0440\u043d\u043e')),
                ('is_precipitation', models.BooleanField(default=False, db_index=True, verbose_name='\u043e\u0441\u0430\u0434\u043a\u0438')),
                ('is_variable', models.BooleanField(default=False, db_index=True, verbose_name='\u043f\u0435\u0440\u0435\u043c\u0435\u043d\u043d\u0430\u044f \u043e\u0431\u043b\u0430\u0447\u043d\u043e\u0441\u0442\u044c')),
                ('is_active', models.BooleanField(default=True, db_index=True, verbose_name='\u0430\u043a\u0442\u0438\u0432\u043d\u043e')),
                ('months', models.ManyToManyField(to='weather.Month', verbose_name='\u043c\u0435\u0441\u044f\u0446\u0430', blank=True)),
            ],
            options={
                'verbose_name': '\u041f\u043e\u0436\u0435\u043b\u0430\u043d\u0438\u0435 \u043f\u043e \u0443\u0441\u043b\u043e\u0432\u0438\u044f\u043c',
                'verbose_name_plural': '\u041f\u043e\u0436\u0435\u043b\u0430\u043d\u0438\u044f \u043f\u043e \u0443\u0441\u043b\u043e\u0432\u0438\u044f\u043c',
            },
        ),
        migrations.CreateModel(
            name='WishForDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 1920x440', upload_to=b'img/site/weather/wishes/', verbose_name='\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('text', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442')),
                ('date', models.DateField(verbose_name='\u0434\u0430\u0442\u0430', db_index=True)),
            ],
            options={
                'verbose_name': '\u043f\u043e\u0436\u0435\u043b\u0430\u043d\u0438\u0435 \u043d\u0430 \u0434\u0435\u043d\u044c',
                'verbose_name_plural': '\u043f\u043e\u0436\u0435\u043b\u0430\u043d\u0438\u044f \u043d\u0430 \u0434\u0435\u043d\u044c',
            },
        ),
        migrations.AlterUniqueTogether(
            name='wishforday',
            unique_together=set([('date',)]),
        ),
        migrations.AlterUniqueTogether(
            name='joke',
            unique_together=set([('month', 'day')]),
        ),
    ]
