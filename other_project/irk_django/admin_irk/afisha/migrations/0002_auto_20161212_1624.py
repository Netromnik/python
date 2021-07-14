# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import irk.afisha.models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
        ('options', '0001_initial'),
        ('afisha', '0001_initial'),
        ('phones', '0002_bankproxy'),
        ('testing', '0001_initial'),
        ('news', '0002_auto_20161212_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('is_announce', models.BooleanField(default=False, help_text='\u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b \u043f\u043e\u043f\u0430\u0434\u0435\u0442 \u0432 \u0441\u043b\u0430\u0439\u0434\u0435\u0440 \u0430\u043d\u043e\u043d\u0441\u043e\u0432', db_index=True, verbose_name='\u0430\u043d\u043e\u043d\u0441\u0438\u0440\u043e\u0432\u0430\u0442\u044c')),
                ('article_ptr', models.OneToOneField(parent_link=True, related_name='afisha_articles', primary_key=True, serialize=False, to='news.Article')),
            ],
            options={
                'verbose_name': '\u0441\u0442\u0430\u0442\u044c\u044f',
                'verbose_name_plural': '\u0441\u0442\u0430\u0442\u044c\u0438',
            },
            bases=('news.article', models.Model),
        ),
        migrations.CreateModel(
            name='CurrentSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0431\u044b\u0442\u0438\u044f', db_index=True)),
                ('time', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f', db_index=True)),
                ('filter_time', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441 \u0443\u0447\u0435\u0442\u043e\u043c \u0434\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u0438', db_index=True)),
                ('fake_date', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0431\u044b\u0442\u0438\u044f', db_index=True)),
                ('real_date', models.DateTimeField(verbose_name='\u0420\u0435\u0430\u043b\u044c\u043d\u0430\u044f \u0434\u0430\u0442\u0430', db_index=True)),
                ('end_date', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f', db_index=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('is_3d', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'afisha_current_sessions',
                'verbose_name': '\u0437\u0430\u043f\u0438\u0441\u044c',
                'verbose_name_plural': '\u043a\u044d\u0448',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('caption', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430', blank=True)),
                ('original_title', models.CharField(max_length=255, verbose_name='\u043e\u0440\u0438\u0433\u0438\u043d\u0430\u043b\u044c\u043d\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('duration', models.CharField(help_text='\u0423\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0434\u043b\u044f \u043a\u0438\u043d\u043e, \u043a\u043e\u043d\u0446\u0435\u0440\u0442\u043e\u0432, \u0441\u043f\u0435\u043a\u0442\u0430\u043a\u043b\u0435\u0439 \u0438 \u0442.\u0434.', max_length=255, null=True, verbose_name='\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c', blank=True)),
                ('production', models.CharField(help_text='\u0423\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0442\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u043a\u0438\u043d\u043e.', max_length=255, verbose_name='\u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e', blank=True)),
                ('info', models.TextField(help_text='\u0420\u0435\u0436\u0438\u0441\u0451\u0440\u044b, \u0430\u043a\u0442\u0451\u0440\u044b. \u0411\u043e\u043b\u0434 \u043d\u0438\u043a\u043e\u0433\u0434\u0430 \u0437\u0434\u0435\u0441\u044c \u043d\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u043c!', verbose_name='\u0414\u043e\u043f. \u0438\u043d\u0444\u043e', blank=True)),
                ('content', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('source_url', models.URLField(help_text='\u0421 http://', verbose_name='\u041e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0430\u0439\u0442', blank=True)),
                ('comments_cnt', models.IntegerField(null=True, editable=False)),
                ('last_comment_id', models.IntegerField(null=True, editable=False)),
                ('video', models.TextField(help_text='HTML \u043a\u043e\u0434', verbose_name='\u0412\u0438\u0434\u0435\u043e', blank=True)),
                ('age_rating', models.SmallIntegerField(default=None, null=True, verbose_name='\u0412\u043e\u0437\u0440\u0430\u0441\u0442\u043d\u043e\u0439 \u0440\u0435\u0439\u0442\u0438\u043d\u0433', blank=True, choices=[(0, b'0+'), (6, b'6+'), (12, b'12+'), (16, b'16+'), (18, b'18+'), (21, b'21+')])),
                ('premiere_date', models.CharField(max_length=255, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u0440\u0435\u043c\u044c\u0435\u0440\u044b', blank=True)),
                ('is_user_added', models.BooleanField(default=False, verbose_name='\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u043e \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u043c')),
                ('is_hidden', models.BooleanField(default=True, verbose_name='\u0421\u043a\u0440\u044b\u0442\u043e')),
                ('author_ip', models.PositiveIntegerField(default=None, null=True, verbose_name='IP \u0430\u0432\u0442\u043e\u0440\u0430', blank=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('buy_btn_clicks', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043b\u0438\u043a\u0438 \u043f\u043e \u043a\u043d\u043e\u043f\u043a\u0435 \u043a\u0443\u043f\u0438\u0442\u044c')),
                ('imdb_id', models.CharField(max_length=10, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0432 IMDB', blank=True)),
                ('imdb_rate', models.FloatField(null=True, verbose_name='\u0420\u0435\u0439\u0442\u0438\u043d\u0433 IMDB', blank=True)),
                ('wide_image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 960\u0445454 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.afisha.models.image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
            ],
            options={
                'verbose_name': '\u0441\u043e\u0431\u044b\u0442\u0438\u0435',
                'verbose_name_plural': '\u0441\u043e\u0431\u044b\u0442\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='EventGuide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guide_name', models.CharField(max_length=255, blank=True)),
                ('main_announcement', models.BooleanField(default=False, verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439')),
                ('event', models.ForeignKey(to='afisha.Event')),
            ],
            options={
                'verbose_name': '\u043f\u0440\u0438\u0432\u044f\u0437\u043a\u0443',
                'verbose_name_plural': '\u043f\u0440\u0438\u0432\u044f\u0437\u043a\u0430',
            },
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('title2', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 (\u0412)', blank=True)),
                ('alias', models.SlugField(verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('position', models.IntegerField(default=0, db_index=True, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', blank=True)),
                ('on_index', models.BooleanField(default=True, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0432 \u0433\u043b\u0430\u0432\u043d\u043e\u0439 \u043b\u0435\u043d\u0442\u0435')),
                ('hide_past', models.BooleanField(default=False, db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0432\u0430\u0442\u044c \u043f\u0440\u043e\u0448\u0435\u0434\u0448\u0438\u0435 \u0441\u043e\u0431\u044b\u0442\u0438\u044f')),
            ],
            options={
                'db_table': 'afisha_sections',
                'verbose_name': '\u0442\u0438\u043f \u0441\u043e\u0431\u044b\u0442\u0438\u044f',
                'verbose_name_plural': '\u0442\u0438\u043f\u044b',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'db_table': 'afisha_genre',
                'verbose_name': '\u0436\u0430\u043d\u0440',
                'verbose_name_plural': '\u0436\u0430\u043d\u0440\u044b',
            },
        ),
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('firms_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='phones.Firms')),
                ('is_active', models.BooleanField(default=True)),
                ('title_short', models.CharField(max_length=255, verbose_name='\u041a\u043e\u0440\u043e\u0442\u043a\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('main_phones', models.CharField(max_length=255, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d\u044b \u0434\u043b\u044f \u0441\u043c\u0441', blank=True)),
                ('kitchen_type', models.CharField(default=0, verbose_name='\u0422\u0438\u043f \u043a\u0443\u0445\u043d\u0438', max_length=255, editable=False)),
                ('price_type', models.IntegerField(default=0, editable=False)),
                ('map', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/afisha/maps', null=True, verbose_name='\u0421\u0445\u0435\u043c\u0430 \u0437\u0430\u043b\u0430', blank=True)),
                ('obed_address', models.CharField(max_length=255, blank=True)),
                ('obed_id', models.IntegerField(null=True, blank=True)),
                ('article', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('menu', models.TextField(verbose_name='\u041c\u0435\u043d\u044e', blank=True)),
                ('skip_tour_for_sms', models.BooleanField(default=False)),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.afisha.models.upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('notice', models.TextField(verbose_name='\u041e\u0431\u044a\u044f\u0432\u043b\u0435\u043d\u0438\u0435', blank=True)),
                ('event_type', models.ForeignKey(verbose_name='\u0422\u0438\u043f \u0441\u043e\u0431\u044b\u0442\u0438\u0439.', to='afisha.EventType', null=True)),
                ('type_main', models.ForeignKey(blank=True, to='phones.Sections', null=True)),
            ],
            options={
                'verbose_name': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f \u0433\u0438\u0434\u0430',
            },
            bases=('phones.firms', models.Model),
        ),
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('num_places', models.PositiveIntegerField(null=True, verbose_name='\u041a\u043e\u043b-\u0432\u043e \u043c\u0435\u0441\u0442', blank=True)),
                ('map', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/afisha/maps', null=True, verbose_name='\u0421\u0445\u0435\u043c\u0430 \u0437\u0430\u043b\u0430', blank=True)),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('notice', models.TextField(verbose_name='\u041e\u0431\u044a\u044f\u0432\u043b\u0435\u043d\u0438\u0435', blank=True)),
                ('position', models.SmallIntegerField(null=True, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('guide', models.ForeignKey(to='afisha.Guide')),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043b',
            },
        ),
        migrations.CreateModel(
            name='KassyBuilding',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440', primary_key=True)),
                ('type_id', models.IntegerField(null=True, verbose_name='id \u0442\u0438\u043f\u0430 \u0443\u0447\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u044f')),
                ('region_id', models.IntegerField(null=True, verbose_name='id \u0440\u0435\u0433\u0438\u043e\u043d\u0430')),
                ('title', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('descr', models.TextField(verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('address', models.CharField(max_length=255, verbose_name='\u0430\u0434\u0440\u0435\u0441')),
                ('phone', models.CharField(max_length=255, verbose_name='\u0442\u0435\u043b\u0435\u0444\u043e\u043d')),
                ('url', models.CharField(max_length=255, verbose_name='\u0441\u0430\u0439\u0442')),
                ('workhrs', models.CharField(max_length=255, verbose_name='\u0447\u0430\u0441\u044b \u0440\u0430\u0431\u043e\u0442\u044b')),
                ('hall_count', models.IntegerField(null=True, verbose_name='\u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0437\u0430\u043b\u043e\u0432')),
                ('marginprc', models.IntegerField(null=True, verbose_name='\u043f\u0440\u043e\u0446\u0435\u043d\u0442 \u043d\u0430\u0446\u0435\u043d\u043a\u0438')),
                ('geo_lat', models.FloatField(null=True, verbose_name='\u0433\u0435\u043e\u0433\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0448\u0438\u0440\u043e\u0442\u0430')),
                ('geo_lng', models.FloatField(null=True, verbose_name='\u0433\u0435\u043e\u0433\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0434\u043e\u043b\u0433\u043e\u0442\u0430')),
                ('is_sale', models.BooleanField(default=True, db_index=True, verbose_name='\u043f\u0440\u043e\u0434\u0430\u0436\u0438 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u044b')),
                ('is_reserv', models.BooleanField(default=True, db_index=True, verbose_name='\u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u043e')),
                ('is_pos', models.BooleanField(default=False, db_index=True, verbose_name='\u0435\u0441\u0442\u044c POS-\u0442\u0435\u0440\u043c\u0438\u043d\u0430\u043b')),
                ('state', models.BooleanField(default=True, db_index=True, verbose_name='\u0430\u043a\u0442\u0438\u0432\u043d\u043e')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('guide', models.OneToOneField(null=True, verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0433\u0438\u0434\u0430', to='afisha.Guide')),
            ],
            options={
                'verbose_name': '\u0443\u0447\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u0435 \u0432 kassy.ru',
                'verbose_name_plural': '\u0443\u0447\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u044f \u0432 kassy.ru',
            },
        ),
        migrations.CreateModel(
            name='KassyEvent',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440', primary_key=True)),
                ('type_id', models.IntegerField(null=True, verbose_name='id \u0442\u0438\u043f\u0430 \u0437\u0440\u0435\u043b\u0438\u0449\u0430')),
                ('kassy_rollerman_id', models.IntegerField(null=True, verbose_name='\u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0442\u043e\u0440', db_index=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('marginprc', models.IntegerField(null=True, verbose_name='\u043f\u0440\u043e\u0446\u0435\u043d\u0442 \u043d\u0430\u0446\u0435\u043d\u043a\u0438')),
                ('duration', models.IntegerField(null=True, verbose_name='\u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c (\u0441\u0435\u043a)')),
                ('age_restriction', models.CharField(max_length=10, verbose_name='\u0432\u043e\u0437\u0440\u0430\u0441\u0442\u043d\u043e\u0435 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435')),
                ('rating', models.IntegerField(null=True, verbose_name='\u0440\u0435\u0439\u0442\u0438\u043d\u0433 \u0432 \u0431\u0430\u043b\u043b\u0430\u0445')),
                ('announce', models.TextField(verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('image', models.URLField(verbose_name='\u0430\u0434\u0440\u0435\u0441 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f')),
                ('is_sale', models.BooleanField(default=True, db_index=True, verbose_name='\u043f\u0440\u043e\u0434\u0430\u0436\u0438 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u044b')),
                ('is_reserv', models.BooleanField(default=True, db_index=True, verbose_name='\u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u043e')),
                ('state', models.BooleanField(default=True, db_index=True, verbose_name='\u0430\u043a\u0442\u0438\u0432\u043d\u043e')),
                ('date_start', models.DateTimeField(null=True, verbose_name='\u0434\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('event', models.ForeignKey(verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435', blank=True, to='afisha.Event', null=True)),
            ],
            options={
                'verbose_name': '\u0441\u043e\u0431\u044b\u0442\u0438\u0435 \u0432 kassy.ru',
                'verbose_name_plural': '\u0441\u043e\u0431\u044b\u0442\u0438\u044f \u0432 kassy.ru',
            },
        ),
        migrations.CreateModel(
            name='KassyHall',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440', primary_key=True)),
                ('kassy_building_id', models.IntegerField(null=True, verbose_name='\u0443\u0447\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u0435', db_index=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('descr', models.TextField(verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('update', models.DateTimeField(null=True, verbose_name='\u0434\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0432 \u0437\u0430\u043b\u0435')),
                ('is_navigated', models.BooleanField(default=False, verbose_name='\u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u043f\u043e \u0441\u0435\u043a\u0446\u0438\u044f\u043c')),
                ('width', models.IntegerField(null=True, verbose_name='\u0448\u0438\u0440\u0438\u043d\u0430 \u043f\u043b\u0430\u043d\u0430 \u0437\u0430\u043b\u0430')),
                ('height', models.IntegerField(null=True, verbose_name='\u0432\u044b\u0441\u043e\u0442\u0430 \u043f\u043b\u0430\u043d\u0430 \u0437\u0430\u043b\u0430')),
                ('hidden', models.BooleanField(default=False, db_index=True, verbose_name='\u0441\u043a\u0440\u044b\u0442')),
                ('state', models.BooleanField(default=True, db_index=True, verbose_name='\u0430\u043a\u0442\u0438\u0432\u043d\u043e')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('hall', models.OneToOneField(null=True, verbose_name='\u0437\u0430\u043b', to='afisha.Hall')),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043b \u0432 kassy.ru',
                'verbose_name_plural': '\u0437\u0430\u043b\u044b \u0432 kassy.ru',
            },
        ),
        migrations.CreateModel(
            name='KassyRollerman',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440', primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('email', models.CharField(max_length=255, verbose_name='email')),
                ('address', models.CharField(max_length=255, verbose_name='\u0430\u0434\u0440\u0435\u0441')),
                ('phone', models.CharField(max_length=255, verbose_name='\u0442\u0435\u043b\u0435\u0444\u043e\u043d')),
                ('inn', models.CharField(max_length=255, verbose_name='\u0418\u041d\u041d')),
                ('okpo', models.CharField(max_length=255, verbose_name='\u041e\u041a\u041f\u041e')),
                ('state', models.BooleanField(default=True, db_index=True, verbose_name='\u0430\u043a\u0442\u0438\u0432\u043d\u043e')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
            ],
            options={
                'verbose_name': '\u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0442\u043e\u0440 \u0432 kassy.ru',
                'verbose_name_plural': '\u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0442\u043e\u0440\u044b \u0432 kassy.ru',
            },
        ),
        migrations.CreateModel(
            name='KassySession',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440', primary_key=True)),
                ('date', models.DateTimeField(verbose_name='\u0434\u0430\u0442\u0430 \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f', db_index=True)),
                ('price_min', models.IntegerField(null=True, verbose_name='\u043c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0446\u0435\u043d\u0430')),
                ('price_max', models.IntegerField(null=True, verbose_name='\u043c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0446\u0435\u043d\u0430')),
                ('vacancies', models.IntegerField(null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u044b\u0445 \u0431\u0438\u043b\u0435\u0442\u043e\u0432')),
                ('is_gst', models.BooleanField(default=True, verbose_name='\u0433\u0430\u0441\u0442\u0440\u043e\u043b\u0438')),
                ('is_prm', models.BooleanField(default=True, verbose_name='\u043f\u0440\u0435\u043c\u044c\u0435\u0440\u0430')),
                ('is_recommend', models.BooleanField(default=True, verbose_name='\u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u0435\u043c\u043e\u0435')),
                ('sale_state', models.IntegerField(default=1, verbose_name='\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u043f\u0440\u043e\u0434\u0430\u0436 \u0441\u043e\u0431\u044b\u0442\u0438\u044f', choices=[(1, '\u0432 \u043f\u0440\u043e\u0434\u0430\u0436\u0435'), (-1, '\u0432 \u043f\u0440\u043e\u0434\u0430\u0436\u0435, \u043d\u043e \u043d\u0435\u0442 \u0434\u043e\u0441\u0442\u0443\u043f\u0430 \u043a \u0442\u0430\u0440\u0438\u0444\u0443'), (-2, '\u043f\u0440\u043e\u0434\u0430\u0436\u0430 \u043d\u0435 \u043d\u0430\u0447\u0430\u0442\u0430 \u0438\u043b\u0438 \u043f\u0440\u0438\u043e\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0430'), (-3, '\u043f\u0440\u043e\u0434\u0430\u0436\u0430 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430')])),
                ('state', models.BooleanField(default=True, db_index=True, verbose_name='\u0430\u043a\u0442\u0438\u0432\u043d\u043e')),
                ('is_ignore', models.BooleanField(default=False, db_index=True, verbose_name='\u0438\u0433\u043d\u043e\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('current_session', models.OneToOneField(related_name='_kassy_session', null=True, verbose_name='\u0441\u0435\u0430\u043d\u0441', to='afisha.CurrentSession')),
                ('kassy_event', models.ForeignKey(verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435', to='afisha.KassyEvent', null=True)),
                ('kassy_hall', models.ForeignKey(verbose_name='\u0437\u0430\u043b', to='afisha.KassyHall', null=True)),
            ],
            options={
                'get_latest_by': 'date',
                'verbose_name': '\u0441\u0435\u0430\u043d\u0441 \u0432 kassy.ru',
                'verbose_name_plural': '\u0441\u0435\u0430\u043d\u0441\u044b \u0432 kassy.ru',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('price', models.CharField(max_length=255, null=True, blank=True)),
                ('is_3d', models.BooleanField(default=False, verbose_name='3D')),
                ('duration', models.TimeField(null=True, verbose_name='\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c', blank=True)),
                ('event_guide', models.ForeignKey(to='afisha.EventGuide')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('is_announce', models.BooleanField(default=False, help_text='\u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b \u043f\u043e\u043f\u0430\u0434\u0435\u0442 \u0432 \u0441\u043b\u0430\u0439\u0434\u0435\u0440 \u0430\u043d\u043e\u043d\u0441\u043e\u0432', db_index=True, verbose_name='\u0430\u043d\u043e\u043d\u0441\u0438\u0440\u043e\u0432\u0430\u0442\u044c')),
                ('photo_ptr', models.OneToOneField(parent_link=True, related_name='afisha_photos', primary_key=True, serialize=False, to='news.Photo')),
            ],
            options={
                'verbose_name': '\u0444\u043e\u0442\u043e\u0440\u0435\u043f\u043e\u0440\u0442\u0430\u0436',
                'verbose_name_plural': '\u0444\u043e\u0442\u043e\u0440\u0435\u043f\u043e\u0440\u0442\u0430\u0436\u0438',
            },
            bases=('news.photo', models.Model),
        ),
        migrations.CreateModel(
            name='Prism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('klass', models.CharField(max_length=20, verbose_name='\u041a\u043b\u0430\u0441\u0441 \u0434\u043b\u044f \u043e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u044f')),
                ('position', models.PositiveSmallIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', blank=True)),
                ('is_hidden', models.BooleanField(default=False, verbose_name='\u0421\u043a\u0440\u044b\u0442\u043e')),
            ],
            options={
                'ordering': ['position', '-id'],
                'verbose_name': '\u043f\u0440\u0438\u0437\u043c\u0430',
                'verbose_name_plural': '\u043f\u0440\u0438\u0437\u043c\u044b',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('is_announce', models.BooleanField(default=False, help_text='\u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b \u043f\u043e\u043f\u0430\u0434\u0435\u0442 \u0432 \u0441\u043b\u0430\u0439\u0434\u0435\u0440 \u0430\u043d\u043e\u043d\u0441\u043e\u0432', db_index=True, verbose_name='\u0430\u043d\u043e\u043d\u0441\u0438\u0440\u043e\u0432\u0430\u0442\u044c')),
                ('article_ptr', models.OneToOneField(parent_link=True, related_name='afisha_reviews', primary_key=True, serialize=False, to='news.Article')),
                ('event', models.ForeignKey(related_name='review', verbose_name='\u0421\u043e\u0431\u044b\u0442\u0438\u0435', to='afisha.Event')),
            ],
            options={
                'db_table': 'afisha_review',
                'verbose_name': '\u0440\u0435\u0446\u0435\u043d\u0437\u0438\u044f',
                'verbose_name_plural': '\u0440\u0435\u0446\u0435\u043d\u0437\u0438\u0438',
            },
            bases=('news.article', models.Model),
        ),
        migrations.CreateModel(
            name='Sessions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.TimeField()),
                ('order_time', models.IntegerField(editable=False, db_index=True)),
                ('period', models.ForeignKey(to='afisha.Period')),
            ],
            options={
                'ordering': ('order_time',),
            },
        ),
        migrations.CreateModel(
            name='GuideFirm',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('phones.firms',),
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
        migrations.CreateModel(
            name='Test',
            fields=[
            ],
            options={
                'verbose_name': '\u0442\u0435\u0441\u0442',
                'proxy': True,
                'verbose_name_plural': '\u0442\u0435\u0441\u0442\u044b \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('testing.test',),
        ),
        migrations.AddField(
            model_name='eventguide',
            name='guide',
            field=models.ForeignKey(verbose_name='\u0413\u0438\u0434', blank=True, to='afisha.Guide', null=True),
        ),
        migrations.AddField(
            model_name='eventguide',
            name='hall',
            field=models.ForeignKey(verbose_name='\u0417\u0430\u043b', blank=True, to='afisha.Hall', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='genre',
            field=models.ForeignKey(db_column=b'genreID', blank=True, to='afisha.Genre', null=True, verbose_name='\u0416\u0430\u043d\u0440'),
        ),
        migrations.AddField(
            model_name='event',
            name='parent',
            field=models.ForeignKey(blank=True, to='afisha.Event', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='prisms',
            field=models.ManyToManyField(related_name='events', verbose_name='\u041f\u0440\u0438\u0437\u043c\u044b', to='afisha.Prism', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='sites',
            field=models.ManyToManyField(related_name='events', db_table=b'afisha_sites_events', verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b\u044b', to='options.Site', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='type',
            field=models.ForeignKey(verbose_name='\u0422\u0438\u043f \u0441\u043e\u0431\u044b\u0442\u0438\u044f', to='afisha.EventType'),
        ),
        migrations.AddField(
            model_name='currentsession',
            name='event',
            field=models.ForeignKey(to='afisha.Event'),
        ),
        migrations.AddField(
            model_name='currentsession',
            name='event_guide',
            field=models.ForeignKey(to='afisha.EventGuide'),
        ),
        migrations.AddField(
            model_name='currentsession',
            name='event_type',
            field=models.ForeignKey(to='afisha.EventType'),
        ),
        migrations.AddField(
            model_name='currentsession',
            name='guide',
            field=models.ForeignKey(to='afisha.Guide', null=True),
        ),
        migrations.AddField(
            model_name='currentsession',
            name='hall',
            field=models.ForeignKey(blank=True, to='afisha.Hall', null=True),
        ),
        migrations.AddField(
            model_name='currentsession',
            name='period',
            field=models.ForeignKey(to='afisha.Period'),
        ),
        migrations.AddField(
            model_name='announcement',
            name='event',
            field=models.ForeignKey(related_name='announcements', verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435', to='afisha.Event'),
        ),
    ]
