# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.map.models
import django.contrib.gis.db.models.fields
from django.conf import settings
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cities',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=180, verbose_name='\u0418\u043c\u044f')),
                ('genitive_name', models.CharField(max_length=180, verbose_name='\u0418\u043c\u044f \u0432 \u0440\u043e\u0434.\u043f.')),
                ('predl_name', models.CharField(max_length=180, verbose_name='\u0418\u043c\u044f \u0432 \u043f\u0440\u0435\u0434\u043b.\u043f.')),
                ('alias', models.CharField(unique=True, max_length=180, verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('accuweather_alias', models.CharField(max_length=100, verbose_name='\u0410\u043b\u0438\u0430\u0441 \u0432 accuweather.com', blank=True)),
                ('order', models.IntegerField(verbose_name='\u041f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0438')),
                ('datif_name', models.CharField(max_length=180, verbose_name='\u0418\u043c\u044f \u0432 \u0434\u0430\u0442.\u043f.', blank=True)),
                ('phones_code', models.IntegerField(verbose_name='\u041a\u043e\u0434 \u0433\u043e\u0440\u043e\u0434\u0430')),
                ('center', django.contrib.gis.db.models.fields.PointField(srid=4326, spatial_index=False, null=True, verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b', blank=True)),
                ('weather_label', django.contrib.gis.db.models.fields.PointField(srid=4326, spatial_index=False, null=True, verbose_name='\u0420\u0430\u0441\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0432 \u043f\u043e\u0433\u043e\u0434\u0435', blank=True)),
                ('is_tourism', models.BooleanField(default=False, verbose_name='\u0422\u0443\u0440\u0438\u0441\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u0433\u043e\u0440\u043e\u0434')),
                ('news_title', models.CharField(max_length=100, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a \u0434\u043b\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439', blank=True)),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0433\u043e\u0440\u043e\u0434\u0430', blank=True)),
                ('cites', models.ManyToManyField(to='options.Site', verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b\u044b', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'cities',
                'verbose_name': '\u0433\u043e\u0440\u043e\u0434',
                'verbose_name_plural': '\u0433\u043e\u0440\u043e\u0434\u0430',
            },
        ),
        migrations.CreateModel(
            name='Cooperative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('point', django.contrib.gis.db.models.fields.PointField(default=b'', srid=4326, spatial_index=False, null=True, verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430')),
                ('city', models.ForeignKey(verbose_name='\u0413\u043e\u0440\u043e\u0434', blank=True, to='map.Cities', null=True)),
            ],
            options={
                'db_table': 'map_cooperative',
                'verbose_name': '\u0433\u0430\u0440\u0430\u0436\u043d\u044b\u0439 \u043a\u043e\u043e\u043f\u0435\u0440\u0430\u0442\u0438\u0432',
                'verbose_name_plural': '\u0433\u0430\u0440\u0430\u0436\u043d\u044b\u0435 \u043a\u043e\u043e\u043f\u0435\u0440\u0430\u0442\u0438\u0432\u044b',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'db_table': 'map_countries',
                'verbose_name': '\u0441\u0442\u0440\u0430\u043d\u0430',
                'verbose_name_plural': '\u0441\u0442\u0440\u0430\u043d\u044b',
            },
        ),
        migrations.CreateModel(
            name='Countryside',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveIntegerField(default=1, verbose_name='\u0422\u0438\u043f', choices=[(1, '\u0441\u0430\u0434\u043e\u0432\u043e\u0434\u0441\u0442\u0432\u043e'), (2, '\u043a\u043e\u0442\u0442\u0435\u0434\u0436\u043d\u044b\u0439 \u043f\u043e\u0441\u0435\u043b\u043e\u043a')])),
                ('tract_distance', models.IntegerField(null=True, verbose_name='\u041a\u0438\u043b\u043e\u043c\u0435\u0442\u0440 \u0442\u0440\u0430\u043a\u0442\u0430', blank=True)),
                ('title', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('point', django.contrib.gis.db.models.fields.PointField(default=b'', srid=4326, spatial_index=False, null=True, verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430')),
                ('city', models.ForeignKey(verbose_name='\u0413\u043e\u0440\u043e\u0434', blank=True, to='map.Cities', null=True)),
            ],
            options={
                'db_table': 'map_countryside',
                'verbose_name': '\u0441\u0430\u0434\u043e\u0432\u043e\u0434\u0441\u0442\u0432\u043e',
                'verbose_name_plural': '\u0441\u0430\u0434\u043e\u0432\u043e\u0434\u0441\u0442\u0432\u0430',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('poly', django.contrib.gis.db.models.fields.PolygonField(default=b'', srid=4326, spatial_index=False, null=True, verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b')),
                ('city', models.ForeignKey(related_name='districts', verbose_name='\u0413\u043e\u0440\u043e\u0434', to='map.Cities')),
                ('parent', models.ForeignKey(verbose_name='\u0420\u043e\u0434\u0438\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0440\u0430\u0439\u043e\u043d', blank=True, to='map.District', null=True)),
            ],
            options={
                'db_table': 'map_districts',
                'verbose_name': '\u0440\u0430\u0439\u043e\u043d',
                'verbose_name_plural': '\u0440\u0430\u0439\u043e\u043d\u044b',
            },
        ),
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('alias', models.SlugField(verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('icon', irk.utils.fields.file.ImageRemovableField(upload_to='img/site/', verbose_name='\u0418\u043a\u043e\u043d\u043a\u0430 \u043c\u0430\u0440\u043a\u0435\u0440\u0430', blank=True)),
                ('visible', models.BooleanField(default=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c')),
                ('default', models.BooleanField(default=False, verbose_name='\u041f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e')),
                ('time_from', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u043f\u043e\u043a\u0430\u0437\u0430', blank=True)),
                ('time_to', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u043e\u043a\u0430\u0437\u0430', blank=True)),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'map_layers',
                'verbose_name': '\u0441\u043b\u043e\u0439',
                'verbose_name_plural': '\u0441\u043b\u043e\u0438',
            },
        ),
        migrations.CreateModel(
            name='MapHouse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('center', django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True)),
                ('poly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'db_table': 'map_houses',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'db_table': 'map_regions',
                'verbose_name': '\u0440\u0435\u0433\u0438\u043e\u043d',
                'verbose_name_plural': '\u0440\u0435\u0433\u0438\u043e\u043d\u044b',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('comments_cnt', models.PositiveIntegerField(default=0, editable=False)),
                ('type', models.PositiveIntegerField(default=0, blank=True, verbose_name='\u0422\u0438\u043f', choices=[(1, '\u041c\u0430\u0440\u0448\u0440\u0443\u0442 \u0442\u0440\u0430\u043d\u0441\u043f\u043e\u0440\u0442\u0430'), (2, '\u0422\u0443\u0440\u0438\u0441\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043c\u0430\u0440\u0448\u0440\u0443\u0442')])),
                ('last_comment_id', models.IntegerField(null=True, editable=False)),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'map_routes',
                'verbose_name': '\u043c\u0430\u0440\u0448\u0440\u0443\u0442',
                'verbose_name_plural': '\u043c\u0430\u0440\u0448\u0440\u0443\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='RoutePoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='\u041a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b')),
                ('route', models.ForeignKey(verbose_name='\u041c\u0430\u0440\u0448\u0440\u0443\u0442', to='map.Route')),
            ],
            options={
                'db_table': 'map_route_points',
                'verbose_name': '\u0442\u043e\u0447\u043a\u0430 \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0430',
                'verbose_name_plural': '\u0442\u043e\u0447\u043a\u0438 \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0430',
            },
        ),
        migrations.CreateModel(
            name='Streets',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('letter', models.IntegerField()),
                ('name', models.CharField(max_length=765)),
                ('name2', models.CharField(max_length=765)),
                ('ntype', models.IntegerField(db_column=b'nType')),
                ('placement', models.CharField(max_length=765)),
                ('wdev_street', models.PositiveIntegerField(null=True, editable=False, blank=True)),
                ('city', models.ForeignKey(to='map.Cities')),
            ],
            options={
                'db_table': 'streets_main',
            },
        ),
        migrations.CreateModel(
            name='Tract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('city', models.ForeignKey(verbose_name='\u0413\u043e\u0440\u043e\u0434', blank=True, to='map.Cities', null=True)),
            ],
            options={
                'db_table': 'map_tracts',
                'verbose_name': '\u0442\u0440\u0430\u043a\u0442',
                'verbose_name_plural': '\u0442\u0440\u0430\u043a\u0442\u044b',
            },
        ),
        migrations.AddField(
            model_name='maphouse',
            name='street',
            field=models.ForeignKey(to='map.Streets'),
        ),
        migrations.AddField(
            model_name='countryside',
            name='tract',
            field=models.ForeignKey(verbose_name='\u0422\u0440\u0430\u043a\u0442', blank=True, to='map.Tract', null=True),
        ),
        migrations.AddField(
            model_name='cities',
            name='region',
            field=models.ForeignKey(verbose_name='\u0420\u0435\u0433\u0438\u043e\u043d', blank=True, to='map.Region', null=True),
        ),
    ]
