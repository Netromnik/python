# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.phones.models
import irk.utils.fields.file
import irk.utils.fields.file
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='A\u0434\u0440\u0435\u0441', blank=True)),
                ('location', models.CharField(max_length=255, verbose_name='\u0414\u043e\u043c', blank=True)),
                ('officenumber', models.CharField(max_length=30, verbose_name='\u041e\u0444\u0438\u0441', db_column=b'officeNumber', blank=True)),
                ('descr', models.CharField(help_text='\u0423\u0442\u043e\u0447\u043d\u0435\u043d\u0438\u0435 \u0434\u043b\u044f \u043f\u043e\u0438\u0441\u043a\u0430 \u043d\u0443\u0436\u043d\u043e\u0433\u043e \u0437\u0434\u0430\u043d\u0438\u044f, \u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: \xab\u043e\u0441\u0442. \u041c\u0438\u043a\u0440\u043e\u0445\u0438\u0440\u0443\u0440\u0433\u0438\u044f \u0433\u043b\u0430\u0437\u0430, \u0437\u0434\u0430\u043d\u0438\u0435 \u042d\u043d\u0435\u0440\u0433\u043e\u043a\u043e\u043b\u043b\u0435\u0434\u0436\u0430\xbb', max_length=255, verbose_name='\u0414\u043e\u043f. \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('streetname', models.CharField(max_length=255, verbose_name='\u0423\u043b\u0438\u0446\u0430', db_column=b'streetName', blank=True)),
                ('is_main', models.BooleanField(default=False, verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0430\u0434\u0440\u0435\u0441')),
                ('priority', models.IntegerField(default=0, editable=False)),
                ('phones', models.CharField(max_length=255, null=True, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d\u044b', blank=True)),
                ('twenty_four_hour', models.BooleanField(default=False, verbose_name='\u041a\u0440\u0443\u0433\u043b\u043e\u0441\u0443\u0442\u043e\u0447\u043d\u043e')),
                ('worktime', models.CharField(max_length=255, verbose_name='\u0427\u0430\u0441\u044b \u0440\u0430\u0431\u043e\u0442\u044b', blank=True)),
                ('map', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/phones/maps/', verbose_name='\u041a\u0430\u0440\u0442\u0430 \u043f\u0440\u043e\u0435\u0437\u0434\u0430', blank=True)),
                ('map_logo', models.BooleanField(default=False, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043b\u043e\u0433\u043e\u0442\u0438\u043f \u043d\u0430 \u043a\u0430\u0440\u0442\u0435')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326, spatial_index=False, null=True, verbose_name='\u0413\u0435\u043e\u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b', blank=True)),
            ],
            options={
                'db_table': 'phones_address',
                'verbose_name': '\u0430\u0434\u0440\u0435\u0441',
                'verbose_name_plural': '\u0430\u0434\u0440\u0435\u0441\u0430',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', irk.utils.fields.file.FileRemovableField(upload_to='img/site', verbose_name='\u0424\u0430\u0439\u043b', blank=True)),
                ('description', models.CharField(max_length=255, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0444\u0430\u0439\u043b\u0430', blank=True)),
            ],
            options={
                'verbose_name': '\u0424\u0430\u0439\u043b \u0434\u043b\u044f \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
                'verbose_name_plural': '\u0424\u0430\u0439\u043b\u044b \u0434\u043b\u044f \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='Firms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.FloatField(default=0, verbose_name='\u0420\u0435\u0439\u0442\u0438\u043d\u0433')),
                ('apteka_id', models.IntegerField(null=True, editable=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('alternative_name', models.CharField(max_length=255, verbose_name='\u0410\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('url', models.CharField(max_length=255, verbose_name='\u0412\u0435\u0431-\u0441\u0430\u0439\u0442', blank=True)),
                ('mail', models.EmailField(max_length=254, verbose_name='E-mail', blank=True)),
                ('skype', models.CharField(max_length=100, null=True, verbose_name='Skype', blank=True)),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('pay_info_until', models.DateTimeField(null=True, editable=False, blank=True)),
                ('pay_top_until', models.DateTimeField(null=True, editable=False, blank=True)),
                ('visible', models.BooleanField(default=False, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c')),
                ('views', models.IntegerField(default=0, editable=False)),
                ('changed', models.BooleanField(default=False, editable=False)),
                ('comments_cnt', models.IntegerField(default=0, editable=False)),
                ('last_comment_id', models.IntegerField(null=True, editable=False)),
                ('logo', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/phones/logo/', null=True, verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f', blank=True)),
                ('map_logo', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 90x50 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/phones/logo/map/', null=True, verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f \u043d\u0430 \u043a\u0430\u0440\u0442\u0435', blank=True)),
                ('app_comment', models.TextField(verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True)),
                ('gis_id', models.IntegerField(null=True, editable=False)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'phones_firms',
                'verbose_name': '\u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u044e',
                'verbose_name_plural': '\u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='MetaSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('alias', models.SlugField(verbose_name='\u0410\u043b\u0438\u0430\u0441')),
            ],
            options={
                'db_table': 'phones_meta_sections',
                'verbose_name': '\u0433\u0440\u0443\u043f\u043f\u0430 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439',
                'verbose_name_plural': '\u0433\u0440\u0443\u043f\u043f\u044b \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439',
            },
        ),
        migrations.CreateModel(
            name='Ownership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=24)),
                ('title_full', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'ordering': ['title'],
                'db_table': 'phones_ownership',
                'verbose_name': '\u0442\u0438\u043f',
                'verbose_name_plural': '\u0442\u0438\u043f\u044b',
            },
        ),
        migrations.CreateModel(
            name='PopularSearch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255, db_index=True)),
                ('searches', models.PositiveIntegerField(default=0, db_index=True)),
                ('results', models.PositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'phones_popular_searches',
                'verbose_name': '\u043f\u043e\u043f\u0443\u043b\u044f\u0440\u043d\u044b\u0439 \u0437\u0430\u043f\u0440\u043e\u0441',
                'verbose_name_plural': '\u043f\u043e\u043f\u0443\u043b\u044f\u0440\u043d\u044b\u0435 \u0437\u0430\u043f\u0440\u043e\u0441\u044b',
            },
        ),
        migrations.CreateModel(
            name='Prices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField()),
                ('price', models.CharField(max_length=30)),
                ('count', models.IntegerField()),
                ('phones_firm_id', models.IntegerField()),
            ],
            options={
                'db_table': 'phones_prices',
            },
        ),
        migrations.CreateModel(
            name='ScanStore',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('type', models.IntegerField(verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[(1, '\u043d\u043e\u0440\u043c'), (2, '\u0438\u0437\u043c\u0435\u043d\u0435\u043d'), (3, '\u043d\u043e\u0432\u044b\u0435'), (5, '\u0443\u0434\u0430\u043b\u0435\u043d\u043d\u044b\u0435'), (4, '\u043e\u0448\u0438\u0431\u043a\u0430')])),
                ('cuption', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('data', models.TextField()),
            ],
            options={
                'verbose_name': '\u0444\u0438\u0440\u043c\u0443',
                'verbose_name_plural': '\u0413\u0440\u0430\u0431\u0431\u0435\u0440',
            },
        ),
        migrations.CreateModel(
            name='Searches',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('query', models.CharField(unique=True, max_length=255)),
                ('count', models.IntegerField()),
                ('result_count', models.IntegerField()),
            ],
            options={
                'db_table': 'phones_searches',
            },
        ),
        migrations.CreateModel(
            name='Sections',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('name_short', models.CharField(max_length=255, verbose_name='\u041a\u043e\u0440\u043e\u0442\u043a\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('slug', models.SlugField(null=True, blank=True, unique=True, verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('css_class', models.SlugField(null=True, verbose_name='\u0421SS \u043a\u043b\u0430\u0441\u0441', blank=True)),
                ('position', models.SmallIntegerField(null=True, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', blank=True)),
                ('views', models.IntegerField(default=0, editable=False)),
                ('org_count', models.IntegerField(default=0, editable=False)),
                ('new_org_count', models.IntegerField(default=0, editable=False)),
                ('logo', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/phones/sections_logo/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f', blank=True)),
                ('is_guide', models.BooleanField(default=False, db_index=True, verbose_name='\u0413\u0438\u0434 \u043f\u043e \u0433\u043e\u0440\u043e\u0434\u0443')),
                ('on_guide_index', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e \u0434\u043b\u044f \u0433\u0438\u0434\u0430')),
                ('in_map', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u0432 \u043f\u0443\u0442\u0435\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u0435 \u043a\u0430\u0440\u0442\u044b')),
                ('in_mobile', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u0432 \u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0445 \u043c\u0435\u0441\u0442\u0430\u0445 \u043e\u0442\u0434\u044b\u0445\u0430')),
                ('place_logo', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/phones/place_logo/', null=True, verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f \u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0445 \u043c\u0435\u0441\u0442', blank=True)),
                ('obed_id', models.IntegerField(blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'phones_sections',
                'verbose_name': '\u0440\u0443\u0431\u0440\u0438\u043a\u0443',
                'verbose_name_plural': '\u0440\u0443\u0431\u0440\u0438\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='UpdateSections',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_id', models.IntegerField()),
                ('title', models.TextField()),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
            ],
            options={
                'db_table': 'phones_update_sections',
            },
        ),
        migrations.CreateModel(
            name='UpdateUrls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=255)),
                ('version', models.IntegerField()),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
                ('is_scanned', models.IntegerField()),
            ],
            options={
                'db_table': 'phones_update_urls',
            },
        ),
        migrations.CreateModel(
            name='VIP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logo', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/phones/firms_vip_logo/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f', blank=True)),
                ('date_from', models.DateField(verbose_name='\u0441')),
                ('date_to', models.DateField(verbose_name='\u043f\u043e')),
            ],
        ),
        migrations.CreateModel(
            name='Worktime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weekday', models.IntegerField(verbose_name='\u0414\u0435\u043d\u044c \u043d\u0435\u0434\u0435\u043b\u0438', choices=[(0, '\u041f\u043e\u043d\u0435\u0434\u0435\u043b\u044c\u043d\u0438\u043a'), (1, '\u0412\u0442\u043e\u0440\u043d\u0438\u043a'), (2, '\u0421\u0440\u0435\u0434\u0430'), (3, '\u0427\u0435\u0442\u0432\u0435\u0440\u0433'), (4, '\u041f\u044f\u0442\u043d\u0438\u0446\u0430'), (5, '\u0421\u0443\u0431\u0431\u043e\u0442\u0430'), (6, '\u0412\u043e\u0441\u043a\u0440\u0435\u0441\u0435\u043d\u044c\u0435')])),
                ('start_time', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0440\u0430\u0431\u043e\u0442\u044b')),
                ('end_time', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0440\u0430\u0431\u043e\u0442\u044b')),
                ('dinner_start_time', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u043e\u0431\u0435\u0434\u0430', blank=True)),
                ('dinner_end_time', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043e\u0431\u0435\u0434\u0430', blank=True)),
                ('start_stamp', models.IntegerField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0440\u0430\u0431\u043e\u0442\u044b \u0432 \u0441\u0435\u043a\u0443\u043d\u0434\u0430\u0445')),
                ('end_stamp', models.IntegerField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0440\u0430\u0431\u043e\u0442\u044b \u0432 \u0441\u0435\u043a\u0443\u043d\u0434\u0430\u0445')),
                ('dinner_start_stamp', models.IntegerField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u043e\u0431\u0435\u0434\u0430 \u0432 \u0441\u0435\u043a\u0443\u043d\u0434\u0430\u0445', blank=True)),
                ('dinner_end_stamp', models.IntegerField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043e\u0431\u0435\u0434\u0430 \u0432 \u0441\u0435\u043a\u0443\u043d\u0434\u0430\u0445', blank=True)),
            ],
            options={
                'verbose_name': '\u0432\u0440\u0435\u043c\u044f \u0440\u0430\u0431\u043e\u0442\u044b',
                'verbose_name_plural': '\u0432\u0440\u0435\u043c\u044f \u0440\u0430\u0431\u043e\u0442\u044b',
            },
        ),
    ]
