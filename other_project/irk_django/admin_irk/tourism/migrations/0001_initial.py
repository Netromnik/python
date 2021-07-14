# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
import irk.utils.fields.file
import dirtyfields.dirtyfields
import irk.tourism.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0001_initial'),
        ('phones', '0002_bankproxy'),
        ('blogs', '0002_auto_20161212_1624'),
        ('news', '0002_auto_20161212_1624'),
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Companion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f')),
                ('about', models.TextField(verbose_name='\u041e \u0441\u0435\u0431\u0435', blank=True)),
                ('my_composition', models.PositiveSmallIntegerField(default=0, verbose_name='\u041c\u043e\u0439 \u0441\u043e\u0441\u0442\u0430\u0432', choices=[(1, b'\xd0\xbc\xd1\x83\xd0\xb6\xd1\x87\xd0\xb8\xd0\xbd\xd0\xb0'), (2, b'\xd0\xb6\xd0\xb5\xd0\xbd\xd1\x89\xd0\xb8\xd0\xbd\xd0\xb0'), (3, b'\xd1\x81\xd0\xb5\xd0\xbc\xd1\x8c\xd1\x8f'), (4, b'\xd0\xba\xd0\xbe\xd0\xbc\xd0\xbf\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8f')])),
                ('find_composition', models.PositiveSmallIntegerField(default=0, verbose_name='\u0418\u0449\u0443 \u0441\u043e\u0441\u0442\u0430\u0432', choices=[(0, b'\xd0\xba\xd0\xbe\xd0\xb3\xd0\xbe \xd1\x83\xd0\xb3\xd0\xbe\xd0\xb4\xd0\xbd\xd0\xbe'), (1, b'\xd0\xbc\xd1\x83\xd0\xb6\xd1\x87\xd0\xb8\xd0\xbd\xd1\x83'), (2, b'\xd0\xb6\xd0\xb5\xd0\xbd\xd1\x89\xd0\xb8\xd0\xbd\xd1\x83'), (3, b'\xd1\x81\xd0\xb5\xd0\xbc\xd1\x8c\xd1\x8e'), (4, b'\xd0\xba\xd0\xbe\xd0\xbc\xd0\xbf\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8e')])),
                ('phone', models.CharField(max_length=255, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d')),
                ('email', models.EmailField(max_length=254, verbose_name='\u041f\u043e\u0447\u0442\u0430')),
                ('place', models.CharField(max_length=255, verbose_name='\u041c\u0435\u0441\u0442\u043e \u043e\u0442\u0434\u044b\u0445\u0430')),
                ('description', models.TextField(verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e', blank=True)),
                ('visible', models.BooleanField(default=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u043d\u0430 \u0441\u0430\u0439\u0442\u0435')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('author', models.ForeignKey(blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='\u0410\u0432\u0442\u043e\u0440')),
            ],
            options={
                'verbose_name': '\u041a\u043e\u043c\u043f\u0430\u043d\u044c\u043e\u043d',
                'verbose_name_plural': '\u041a\u043e\u043c\u043f\u0430\u043d\u044c\u043e\u043d\u044b',
            },
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('firms_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='phones.Firms')),
                ('is_active', models.BooleanField(default=True)),
                ('price', models.CharField(max_length=50, null=True, verbose_name='\u0426\u0435\u043d\u0430', blank=True)),
                ('price_comment', models.CharField(max_length=255, null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043a \u0446\u0435\u043d\u0435', blank=True)),
                ('promo', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442 (\u0441\u043f\u043e\u043d\u0441\u043e\u0440\u0441\u0442\u0432\u043e)', blank=True)),
                ('level', models.PositiveSmallIntegerField(null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0437\u0432\u0435\u0437\u0434', blank=True)),
                ('category', models.CharField(max_length=255, null=True, verbose_name='\u0426\u0435\u043d\u043e\u0432\u0430\u044f \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f', blank=True)),
                ('season', models.CharField(max_length=255, null=True, verbose_name='\u0421\u0435\u0437\u043e\u043d \u0440\u0430\u0431\u043e\u0442\u044b', blank=True)),
                ('is_recommended', models.BooleanField(default=False, verbose_name='\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u043e\u0432\u0430\u043d\u043e')),
            ],
            options={
                'db_table': 'tourism_hotel',
                'verbose_name': '\u0413\u043e\u0441\u0442\u0438\u043d\u0438\u0446\u0430',
                'verbose_name_plural': '\u0413\u043e\u0441\u0442\u0438\u043d\u0438\u0446\u044b',
            },
            bases=('phones.firms',),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, verbose_name='\u0424.\u0418.\u041e.', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone', models.CharField(max_length=255, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d')),
                ('info', models.TextField(verbose_name='\u0414\u043e\u043f. \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f')),
                ('date', models.CharField(max_length=255, verbose_name='\u0414\u0430\u0442\u0430')),
                ('amount', models.CharField(max_length=255, null=True, verbose_name='\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c', blank=True)),
                ('way', models.CharField(max_length=255, verbose_name='\u041a\u0443\u0434\u0430')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043a\u0430\u0437 \u0442\u0443\u0440\u0430',
                'verbose_name_plural': '\u0437\u0430\u043a\u0430\u0437\u044b \u0442\u0443\u0440\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('type', models.PositiveSmallIntegerField(verbose_name='\u0422\u0438\u043f', choices=[(1, '\u0417\u0430\u0440\u0443\u0431\u0435\u0436'), (0, '\u0420\u043e\u0441\u0441\u0438\u044f'), (2, '\u0411\u0430\u0439\u043a\u0430\u043b')])),
                ('short', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430')),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('extra_description', models.TextField(help_text='\u0414\u043b\u044f \u0432\u0438\u0434\u0435\u043e \u0441 YouTube, \u0435\u0441\u043b\u0438 \u0432 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0438 \u043d\u0430\u0445\u043e\u0434\u044f\u0442\u0441\u044f \u0434\u0430\u043d\u043d\u044b\u0435 \u043e\u0442 tonkosti.ru', verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0435 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('content_html', models.BooleanField(default=False, verbose_name='HTML \u0432 \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0438')),
                ('position', models.PositiveSmallIntegerField(verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', blank=True)),
                ('comments_cnt', models.PositiveIntegerField(default=0, editable=False)),
                ('last_comment_id', models.IntegerField(null=True, editable=False)),
                ('is_main', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')),
                ('is_recommended', models.BooleanField(default=False, db_index=True, verbose_name='\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u043e\u0432\u0430\u043d\u043e')),
                ('yahoo_weather_code', models.CharField(help_text='\u0414\u043b\u044f \u043f\u043e\u0433\u043e\u0434\u044b (http://weather.yahoo.com/)', max_length=20, verbose_name='\u041a\u043e\u0434 \u0433\u043e\u0440\u043e\u0434\u0430', blank=True)),
                ('weather_popular', models.BooleanField(default=False, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0432 \u0440\u0430\u0437\u0434\u0435\u043b\u0435 \xab\u041f\u043e\u0433\u043e\u0434\u0430\xbb')),
                ('tonkosti_place_type', models.PositiveIntegerField(default=1, blank=True, verbose_name='\u0422\u0438\u043f \u043c\u0435\u0441\u0442\u0430', choices=[(0, '\u0421\u0442\u0440\u0430\u043d\u0430'), (1, '\u0420\u0435\u0433\u0438\u043e\u043d/\u043a\u0443\u0440\u043e\u0440\u0442')])),
                ('tonkosti_id', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u0434 \u043c\u0435\u0441\u0442\u0430 \u043d\u0430 tonkosti.ru', blank=True)),
                ('center', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, spatial_index=False, blank=True)),
                ('flag', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/tourism/place/', null=True, verbose_name='\u0424\u043b\u0430\u0433', blank=True)),
                ('panorama_url', models.URLField(help_text='\u0422\u043e\u043b\u044c\u043a\u043e \u0441\u0441\u044b\u043b\u043a\u0430, \u0431\u0435\u0437 HTML \u0442\u0435\u0433\u0430 &lt;iframe&gt;', verbose_name='\u0410\u0434\u0440\u0435\u0441 \u043f\u0430\u043d\u043e\u0440\u0430\u043c\u044b', blank=True)),
                ('country', models.ForeignKey(verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430', to='map.Country')),
                ('nearby', models.ManyToManyField(related_name='_place_nearby_+', verbose_name='\u0420\u044f\u0434\u043e\u043c', to='tourism.Place', blank=True)),
                ('parent', models.ForeignKey(related_name='children', verbose_name='\u0420\u043e\u0434\u0438\u0442\u0435\u043b\u044c\u0441\u043a\u0430\u044f \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f', blank=True, to='tourism.Place', null=True)),
            ],
            options={
                'ordering': ['title', 'position'],
                'db_table': 'tourism_places',
                'verbose_name': '\u043c\u0435\u0441\u0442\u043e \u043e\u0442\u0434\u044b\u0445\u0430',
                'verbose_name_plural': '\u043c\u0435\u0441\u0442\u0430 \u043e\u0442\u0434\u044b\u0445\u0430',
            },
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='\u041d\u0435 \u0431\u043e\u043b\u0435\u0435 60 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432', max_length=60, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('short', models.CharField(help_text='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f \u0432 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430\u0445 \u043f\u043e\u0438\u0441\u043a\u0430. \u041d\u0435 \u0431\u043e\u043b\u0435\u0435 80 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432', max_length=80, verbose_name='\u041a\u0440\u0430\u0442\u043a\u043e\u0435 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('price', models.PositiveIntegerField(help_text='\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: 42000', verbose_name='\u0426\u0435\u043d\u0430', db_index=True)),
                ('nights', models.CharField(help_text='\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: 10 \u0434\u043d\u0435\u0439/11 \u043d\u043e\u0447\u0435\u0439', max_length=30, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043d\u043e\u0447\u0435\u0439')),
                ('is_hot', models.BooleanField(default=False, db_index=True, verbose_name='\u0413\u043e\u0440\u044f\u0449\u0438\u0439 \u0442\u0443\u0440')),
                ('is_recommended', models.BooleanField(default=False, db_index=True, verbose_name='\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u043e\u0432\u0430\u043d\u043e')),
                ('file', models.FileField(upload_to=irk.tourism.models.tour_file_upload_to, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('views_cnt', models.PositiveIntegerField(default=False, editable=False)),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c\u044b\u0435 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 \u0434\u043e\u043b\u0436\u043d\u044b \u0431\u044b\u0442\u044c \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 jpeg, gif, png. \u0420\u0430\u0437\u043c\u0435\u0440 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 \u043f\u043e \u0448\u0438\u0440\u0438\u043d\u0435 - 220px, \u043f\u043e \u0432\u044b\u0441\u043e\u0442\u0435 - 145px.', upload_to=b'img/site/tourism/tour/', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True)),
                ('is_hidden', models.BooleanField(default=True, db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0442\u043e')),
            ],
            options={
                'db_table': 'tourism_tours',
                'verbose_name': '\u0422\u0443\u0440',
                'verbose_name_plural': '\u0422\u0443\u0440\u044b',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TourBase',
            fields=[
                ('firms_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='phones.Firms')),
                ('is_active', models.BooleanField(default=True)),
                ('price', models.CharField(max_length=50, null=True, verbose_name='\u0426\u0435\u043d\u0430', blank=True)),
                ('price_comment', models.CharField(max_length=255, null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043a \u0446\u0435\u043d\u0435', blank=True)),
                ('promo', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442 (\u0441\u043f\u043e\u043d\u0441\u043e\u0440\u0441\u0442\u0432\u043e)', blank=True)),
                ('is_recommended', models.BooleanField(default=False, verbose_name='\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u043e\u0432\u0430\u043d\u043e')),
                ('center', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, spatial_index=False, blank=True)),
                ('season', models.CharField(max_length=255, null=True, verbose_name='\u0421\u0435\u0437\u043e\u043d \u0440\u0430\u0431\u043e\u0442\u044b', blank=True)),
                ('place', models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u043e\u0442\u0434\u044b\u0445\u0430', blank=True, to='tourism.Place', null=True)),
            ],
            options={
                'db_table': 'tourism_tourbases',
                'verbose_name': '\u0442\u0443\u0440\u0431\u0430\u0437\u0443',
                'verbose_name_plural': '\u0422\u0443\u0440\u0431\u0430\u0437\u044b',
            },
            bases=('phones.firms',),
        ),
        migrations.CreateModel(
            name='TourDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430')),
                ('tour', models.ForeignKey(to='tourism.Tour')),
            ],
            options={
                'db_table': 'tourism_tour_periods',
                'verbose_name': '\u0434\u0430\u0442\u0430',
                'verbose_name_plural': '\u0434\u0430\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='TourFirm',
            fields=[
                ('firms_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='phones.Firms')),
                ('is_active', models.BooleanField(default=True)),
                ('price', models.CharField(max_length=50, null=True, verbose_name='\u0426\u0435\u043d\u0430', blank=True)),
                ('price_comment', models.CharField(max_length=255, null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043a \u0446\u0435\u043d\u0435', blank=True)),
                ('promo', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442 (\u0441\u043f\u043e\u043d\u0441\u043e\u0440\u0441\u0442\u0432\u043e)', blank=True)),
                ('tour_order', models.BooleanField(default=False, verbose_name='\u0417\u0430\u043a\u0430\u0437 \u0442\u0443\u0440\u0430')),
                ('base', models.ForeignKey(verbose_name='\u0422\u0443\u0440\u0431\u0430\u0437\u0430', blank=True, to='tourism.TourBase', null=True)),
                ('place', models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u043e\u0442\u0434\u044b\u0445\u0430', blank=True, to='tourism.Place', null=True)),
            ],
            options={
                'db_table': 'tourism_tourfirms',
                'verbose_name': '\u0442\u0443\u0440\u0444\u0438\u0440\u043c\u0443',
                'verbose_name_plural': '\u0422\u0443\u0440\u0444\u0438\u0440\u043c\u044b',
            },
            bases=('phones.firms',),
        ),
        migrations.CreateModel(
            name='TourHotel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveSmallIntegerField(verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0432 \u0442\u0443\u0440\u0435', editable=False)),
                ('hotel', models.ForeignKey(verbose_name='\u0413\u043e\u0441\u0442\u0438\u043d\u0438\u0446\u0430', to='tourism.Hotel')),
                ('tour', models.ForeignKey(to='tourism.Tour')),
            ],
            options={
                'db_table': 'tourism_tour_hotels',
                'verbose_name': '\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430',
                'verbose_name_plural': '\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='Way',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trip', models.CharField(max_length=255, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('place', models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u043e\u0442\u0434\u044b\u0445\u0430', to='tourism.Place')),
            ],
            options={
                'db_table': 'tourism_place_ways',
                'verbose_name': '\u041c\u0430\u0440\u0448\u0440\u0443\u0442',
                'verbose_name_plural': '\u041a\u0430\u043a \u0434\u043e\u0431\u0440\u0430\u0442\u044c\u0441\u044f',
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
            ],
            options={
                'verbose_name': '\u0441\u0442\u0430\u0442\u044c\u044f',
                'proxy': True,
                'verbose_name_plural': '\u0441\u0442\u0430\u0442\u044c\u0438 \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('news.article',),
        ),
        migrations.CreateModel(
            name='Infographic',
            fields=[
            ],
            options={
                'verbose_name': '\u0438\u043d\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430',
                'proxy': True,
                'verbose_name_plural': '\u0438\u043d\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430 \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('news.infographic',),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
            ],
            options={
                'verbose_name': '\u043d\u043e\u0432\u043e\u0441\u0442\u044c',
                'proxy': True,
                'verbose_name_plural': '\u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('news.news',),
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
            ],
            options={
                'verbose_name': '\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435',
                'proxy': True,
                'verbose_name_plural': '\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u044f \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('polls.poll',),
        ),
        migrations.AddField(
            model_name='tour',
            name='firm',
            field=models.ForeignKey(verbose_name='\u0424\u0438\u0440\u043c\u0430', to='phones.Firms'),
        ),
        migrations.AddField(
            model_name='tour',
            name='hotels',
            field=models.ManyToManyField(related_name='tours', through='tourism.TourHotel', to='tourism.Hotel'),
        ),
        migrations.AddField(
            model_name='tour',
            name='place',
            field=models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u043e\u0442\u0434\u044b\u0445\u0430', blank=True, to='tourism.Place', null=True),
        ),
        # 11.09.2018 - если не работают миграции туризма, закомментируйте ниже
        #migrations.AddField(
            #model_name='tour',
            #name='transport',
            #field=models.ForeignKey(verbose_name='\u0422\u0440\u0430\u043d\u0441\u043f\u043e\u0440\u0442', blank=True, to='transport.Type', null=True),
        #),
        #migrations.AddField(
            #model_name='place',
            #name='promo',
            #field=models.ForeignKey(related_name='promo_place', blank=True, to='phones.Firms', null=True),
        #),
        #migrations.AddField(
            #model_name='place',
            #name='routes',
            #field=models.ManyToManyField(related_name='places', verbose_name='\u041c\u0430\u0440\u0448\u0440\u0443\u0442\u044b', to='map.Route', blank=True),
        #),
        #migrations.AddField(
            #model_name='order',
            #name='tour_firms',
            #field=models.ManyToManyField(related_name='tour_firms', verbose_name='\u0422\u0443\u0440\u0444\u0438\u0440\u043c\u044b', to='tourism.TourFirm'),
        #),
        #migrations.AddField(
            #model_name='hotel',
            #name='place',
            #field=models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u043e\u0442\u0434\u044b\u0445\u0430', blank=True, to='tourism.Place', null=True),
        #),
    ]
