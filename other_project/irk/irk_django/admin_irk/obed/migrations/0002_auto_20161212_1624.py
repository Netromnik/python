# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.obed.models
import irk.utils.fields.file
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('testing', '0001_initial'),
        ('phones', '0002_bankproxy'),
        ('news', '0002_auto_20161212_1624'),
        ('polls', '0001_initial'),
        ('obed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('article_ptr', models.OneToOneField(parent_link=True, related_name='obed_article', primary_key=True, serialize=False, to='news.Article')),
                ('main_announcement', models.BooleanField(default=True, db_index=True, verbose_name='\u0410\u043d\u043e\u043d\u0441\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')),
            ],
            options={
                'abstract': False,
                'db_table': 'obed_articles',
                'verbose_name': '\u0441\u0442\u0430\u0442\u044c\u044f',
                'verbose_name_plural': '\u0441\u0442\u0430\u0442\u044c\u0438',
            },
            bases=('news.article',),
        ),
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('slug', models.SlugField()),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
            ],
            options={
                'db_table': 'obed_article_categories',
                'verbose_name': '\u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0441\u0442\u0430\u0442\u0435\u0439',
                'verbose_name_plural': '\u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 \u0441\u0442\u0430\u0442\u0435\u0439',
            },
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('caption', models.CharField(max_length=40, verbose_name='\u043f\u043e\u0434\u043f\u0438\u0441\u044c', blank=True)),
                ('css_class', models.CharField(max_length=50, verbose_name='css \u0441\u0442\u0438\u043b\u044c', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u0430')),
            ],
            options={
                'verbose_name': '\u043d\u0430\u0433\u0440\u0430\u0434\u0430',
                'verbose_name_plural': '\u043d\u0430\u0433\u0440\u0430\u0434\u044b',
            },
        ),
        migrations.CreateModel(
            name='Corporative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': '\u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432',
                'verbose_name_plural': '\u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u044b',
            },
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('price', models.IntegerField(default=0, null=True, verbose_name='\u0426\u0435\u043d\u0430', blank=True)),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('mark', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u041e\u0446\u0435\u043d\u043a\u0430', choices=[(1, '\u0423\u0436\u0430\u0441\u043d\u043e'), (2, '\u041f\u043b\u043e\u0445\u043e'), (3, '\u041d\u0438\u0436\u0435 \u0441\u0440\u0435\u0434\u043d\u0435\u0433\u043e'), (4, '\u0425\u043e\u0440\u043e\u0448\u043e'), (5, '\u041e\u0442\u043b\u0438\u0447\u043d\u043e')])),
            ],
            options={
                'verbose_name': '\u0431\u043b\u044e\u0434\u043e',
                'verbose_name_plural': '\u0431\u043b\u044e\u0434\u0430',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'verbose_name': '\u0440\u0430\u0439\u043e\u043d',
                'verbose_name_plural': '\u0440\u0430\u0439\u043e\u043d\u044b',
            },
        ),
        migrations.CreateModel(
            name='Establishment',
            fields=[
                ('firms_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='phones.Firms')),
                ('is_active', models.BooleanField(default=True)),
                ('obed_id', models.IntegerField(null=True, verbose_name='ID-\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0441 obed.irk.ru', blank=True)),
                ('old_establishment_id', models.IntegerField(null=True, verbose_name='ID-\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0439 \u0434\u043e \u0440\u0435\u0444\u0430\u043a\u0442\u043e\u0440\u0438\u043d\u0433\u0430', blank=True)),
                ('contacts', models.CharField(max_length=1000, null=True, verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438')),
                ('wifi', models.BooleanField(default=False, db_index=True, verbose_name='Wi-Fi')),
                ('dancing', models.BooleanField(default=False, db_index=True, verbose_name='\u0422\u0430\u043d\u0446\u043f\u043e\u043b')),
                ('karaoke', models.BooleanField(default=False, db_index=True, verbose_name='\u041a\u0430\u0440\u0430\u043e\u043a\u0435')),
                ('children_room', models.BooleanField(default=False, db_index=True, verbose_name='\u0414\u0435\u0442\u0441\u043a\u0430\u044f \u043a\u043e\u043c\u043d\u0430\u0442\u0430')),
                ('terrace', models.BooleanField(default=False, db_index=True, verbose_name='\u041b\u0435\u0442\u043d\u044f\u044f \u0432\u0435\u0440\u0430\u043d\u0434\u0430')),
                ('catering', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0435\u0437\u0434\u043d\u043e\u0435 \u043e\u0431\u0441\u043b\u0443\u0436\u0438\u0432\u0430\u043d\u0438\u0435')),
                ('business_lunch', models.BooleanField(default=False, db_index=True, verbose_name='\u0411\u0438\u0437\u043d\u0435\u0441-\u043b\u0430\u043d\u0447')),
                ('business_lunch_price', models.PositiveIntegerField(db_index=True, null=True, verbose_name='\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0431\u0438\u0437\u043d\u0435\u0441-\u043b\u0430\u043d\u0447\u0430', blank=True)),
                ('business_lunch_time', models.CharField(max_length=30, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0431\u0438\u0437\u043d\u0435\u0441-\u043b\u0430\u043d\u0447\u0430', blank=True)),
                ('cooking_class', models.BooleanField(default=False, db_index=True, verbose_name='\u041a\u0443\u043b\u0438\u043d\u0430\u0440\u043d\u044b\u0435 \u043c\u0430\u0441\u0442\u0435\u0440-\u043a\u043b\u0430\u0441\u0441\u044b')),
                ('breakfast', models.BooleanField(default=False, db_index=True, verbose_name='\u0417\u0430\u0432\u0442\u0440\u0430\u043a')),
                ('children_menu', models.BooleanField(default=False, db_index=True, verbose_name='\u0414\u0435\u0442\u0441\u043a\u043e\u0435 \u043c\u0435\u043d\u044e')),
                ('cashless', models.BooleanField(default=True, db_index=True, verbose_name='\u0411\u0435\u0437\u043d\u0430\u043b')),
                ('live_music', models.BooleanField(default=False, db_index=True, verbose_name='\u0416\u0438\u0432\u0430\u044f \u043c\u0443\u0437\u044b\u043a\u0430')),
                ('entertainment', models.BooleanField(default=False, db_index=True, verbose_name='\u0420\u0430\u0437\u0432\u043b\u0435\u043a\u0430\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0430')),
                ('banquet_hall', models.BooleanField(default=False, db_index=True, verbose_name='\u0411\u0430\u043d\u043a\u0435\u0442\u043d\u044b\u0439 \u0437\u0430\u043b')),
                ('parking', models.CharField(max_length=255, null=True, verbose_name='\u041f\u0430\u0440\u043a\u043e\u0432\u043a\u0430', blank=True)),
                ('facecontrol', models.CharField(max_length=255, null=True, verbose_name='\u0412\u0445\u043e\u0434', blank=True)),
                ('bill', models.PositiveIntegerField(db_index=True, null=True, verbose_name='\u0421\u0440\u0435\u0434\u043d\u0438\u0439 \u0447\u0435\u043a', choices=[(1, '\u0434\u043e 500 \u0440.'), (2, '\u043e\u0442 500 \u0434\u043e 1000 \u0440.'), (3, '\u043e\u0442 1000 \u0434\u043e 1500 \u0440.'), (4, '\u0431\u043e\u043b\u044c\u0448\u0435 1500 \u0440.')])),
                ('virtual_tour', models.CharField(max_length=255, null=True, verbose_name='\u0412\u0438\u0440\u0442\u0443\u0430\u043b\u044c\u043d\u044b\u0439 \u0442\u0443\u0440', blank=True)),
                ('total_user_rating', models.FloatField(default=0, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u0440\u0435\u0439\u0442\u0438\u043d\u0433', editable=False, db_index=True)),
                ('total_editor_rating', models.FloatField(default=0, verbose_name='\u0420\u0435\u0434\u0430\u043a\u0442\u043e\u0440\u0441\u043a\u0438\u0439 \u0440\u0435\u0439\u0442\u0438\u043d\u0433', editable=False, db_index=True)),
                ('card_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 298\xd7140 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/obed/establishment/', null=True, verbose_name='\u0424\u043e\u0442\u043e \u0434\u043b\u044f \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('corporative', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u0432 \u0441\u043f\u0438\u0441\u043a\u0435 \u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u0430')),
                ('corporative_guest', models.IntegerField(null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0433\u043e\u0441\u0442\u0435\u0439', blank=True)),
                ('corporative_price', models.IntegerField(null=True, verbose_name='\u0426\u0435\u043d\u0430 \u0437\u0430 \u0447\u0435\u043b\u043e\u0432\u0435\u043a\u0430', blank=True)),
                ('corporative_description', models.TextField(null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('corporative_image', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/obed/corporative', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True)),
                ('is_new', models.BooleanField(default=False, db_index=True, verbose_name='\u041d\u043e\u0432\u043e\u0435')),
            ],
            options={
                'verbose_name': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f',
            },
            bases=('phones.firms',),
        ),
        migrations.CreateModel(
            name='GuruCause',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('is_dinner', models.BooleanField(default=False, help_text='\u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0432 \u0444\u0438\u043b\u044c\u0442\u0440\u0435 "\u0423\u0436\u0438\u043d"', db_index=True, verbose_name='\u0443\u0436\u0438\u043d')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': '\u0437\u0430\u043f\u0438\u0441\u044c',
                'verbose_name_plural': '\u0413\u0443\u0440\u0443 (\u043f\u043e\u0432\u043e\u0434)',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': '\u043c\u0435\u043d\u044e \u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f',
                'verbose_name_plural': '\u043c\u0435\u043d\u044e \u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='MenuOfDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('description', models.CharField(max_length=160, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
                ('start_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', db_index=True)),
                ('end_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f', db_index=True)),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c\u044b\u0435 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 \u0434\u043e\u043b\u0436\u043d\u044b \u0431\u044b\u0442\u044c \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 jpeg, gif, png. \u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u0435\u043c\u044b\u0439 \u0440\u0430\u0437\u043c\u0435\u0440 \u043f\u043e \u0448\u0438\u0440\u0438\u043d\u0435 - 620px, \u043f\u043e \u0432\u044b\u0441\u043e\u0442\u0435 - 310px.', upload_to=b'img/site/obed/menuofday', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True)),
            ],
            options={
                'db_table': 'obed_menu_of_day',
                'verbose_name': '\u041c\u0435\u043d\u044e \u0434\u043d\u044f',
                'verbose_name_plural': '\u041c\u0435\u043d\u044e \u0434\u043d\u044f',
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(verbose_name='\u0441\u0441\u044b\u043b\u043a\u0430')),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 620\u0445294 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to='img/site', verbose_name='\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('title', models.CharField(max_length=255, verbose_name='\u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True)),
                ('caption', models.TextField(verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('start_date', models.DateField(verbose_name='\u0434\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', db_index=True)),
                ('end_date', models.DateField(verbose_name='\u0434\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f', db_index=True)),
                ('is_visible', models.BooleanField(default=False, db_index=True, verbose_name='\u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f')),
            ],
            options={
                'verbose_name': '\u0420\u0435\u043a\u043b\u0430\u043c\u043d\u043e\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0420\u0435\u043a\u043b\u0430\u043c\u043d\u044b\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('start_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u0430\u043a\u0446\u0438\u0438', db_index=True)),
                ('end_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0430\u043a\u0446\u0438\u0438', db_index=True)),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('content', models.TextField(null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
            ],
            options={
                'verbose_name': '\u0430\u043a\u0446\u0438\u044f',
                'verbose_name_plural': '\u0430\u043a\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='TastyStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
                ('is_hot', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')),
                ('is_hidden', models.BooleanField(default=True, db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0442\u0430\u044f')),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c\u044b\u0435 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 \u0434\u043e\u043b\u0436\u043d\u044b \u0431\u044b\u0442\u044c \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 jpeg, gif, png. \u0420\u0430\u0437\u043c\u0435\u0440 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 \u043f\u043e \u0448\u0438\u0440\u0438\u043d\u0435 - 220px, \u043f\u043e \u0432\u044b\u0441\u043e\u0442\u0435 - 145px.', upload_to=b'img/site/obed/stories', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True)),
                ('firm', models.ForeignKey(verbose_name='\u0424\u0438\u0440\u043c\u0430', to='phones.Firms')),
            ],
            options={
                'db_table': 'obed_tasty_stories',
                'verbose_name': '\u0412\u043a\u0443\u0441\u043d\u0430\u044f \u0438\u0441\u0442\u043e\u0440\u0438\u044f',
                'verbose_name_plural': '\u0412\u043a\u0443\u0441\u043d\u044b\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.obed.models.type_upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('firm_count', models.PositiveIntegerField(null=True, editable=False)),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': '\u0442\u0438\u043f',
                'verbose_name_plural': '\u0442\u0438\u043f\u044b',
            },
        ),
        migrations.CreateModel(
            name='UserRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kitchen', models.PositiveSmallIntegerField(default=0, verbose_name='\u043e\u0446\u0435\u043d\u043a\u0430 \u043a\u0443\u0445\u043d\u0438')),
                ('service', models.PositiveSmallIntegerField(default=0, verbose_name='\u043e\u0446\u0435\u043d\u043a\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u0430')),
                ('environment', models.PositiveSmallIntegerField(default=0, verbose_name='\u043e\u0446\u0435\u043d\u043a\u0430 \u043e\u0431\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='\u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0430')),
                ('user', models.ForeignKey(related_name='obed_establishment_rates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'obed_user_rates',
                'verbose_name': '\u043e\u0446\u0435\u043d\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f',
                'verbose_name_plural': '\u043e\u0446\u0435\u043d\u043a\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
            },
        ),
        migrations.CreateModel(
            name='UserRateHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u0430')),
                ('kitchen', models.FloatField(default=0, verbose_name='\u043e\u0446\u0435\u043d\u043a\u0430 \u043a\u0443\u0445\u043d\u0438')),
                ('service', models.FloatField(default=0, verbose_name='\u043e\u0446\u0435\u043d\u043a\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u0430')),
                ('environment', models.FloatField(default=0, verbose_name='\u043e\u0446\u0435\u043d\u043a\u0430 \u043e\u0431\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438')),
                ('user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created',
                'verbose_name': '\u0438\u0441\u0442\u043e\u0440\u0438\u044f \u043e\u0446\u0435\u043d\u043e\u043a \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
                'verbose_name_plural': '\u0438\u0441\u0442\u043e\u0440\u0438\u0438 \u043e\u0446\u0435\u043d\u043e\u043a \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
                'db_table': 'obed_user_rates_history',
            },
        ),
        migrations.CreateModel(
            name='UserRatingHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True, verbose_name='\u0434\u0430\u0442\u0430')),
                ('kitchen', models.FloatField(default=0, verbose_name='\u0441\u0440\u0435\u0434\u043d\u044f\u044f \u043e\u0446\u0435\u043d\u043a\u0430 \u043a\u0443\u0445\u043d\u0438')),
                ('service', models.FloatField(default=0, verbose_name='\u0441\u0440\u0435\u0434\u043d\u044f\u044f \u043e\u0446\u0435\u043d\u043a\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u0430')),
                ('environment', models.FloatField(default=0, verbose_name='\u0441\u0440\u0435\u0434\u043d\u044f\u044f \u043e\u0446\u0435\u043d\u043a\u0430 \u043e\u0431\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438')),
                ('total', models.FloatField(default=0, verbose_name='\u0438\u0442\u043e\u0433\u043e\u0432\u0430\u044f \u043e\u0446\u0435\u043d\u043a\u0430')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='\u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0433\u043e\u043b\u043e\u0441\u043e\u0432')),
            ],
            options={
                'get_latest_by': 'date',
                'verbose_name': '\u0438\u0441\u0442\u043e\u0440\u0438\u044f \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
                'verbose_name_plural': '\u0438\u0441\u0442\u043e\u0440\u0438\u0438 \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u043e\u0432 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
                'db_table': 'obed_user_rating_history',
            },
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
        migrations.CreateModel(
            name='Review',
            fields=[
                ('obed_article_ptr', models.OneToOneField(parent_link=True, related_name='obed_review', primary_key=True, serialize=False, to='obed.Article')),
                ('kitchen', models.SmallIntegerField(default=0, verbose_name='\u041e\u0446\u0435\u043d\u043a\u0430 \u043a\u0443\u0445\u043d\u0438')),
                ('service', models.SmallIntegerField(default=0, verbose_name='\u041e\u0446\u0435\u043d\u043a\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u0430')),
                ('environment', models.SmallIntegerField(default=0, verbose_name='\u041e\u0446\u0435\u043d\u043a\u0430 \u043e\u0431\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438')),
                ('total', models.FloatField(default=0, verbose_name='\u0438\u0442\u043e\u0433\u043e\u0432\u0430\u044f \u043e\u0446\u0435\u043d\u043a\u0430')),
                ('conclusion', models.TextField(verbose_name='\u0417\u0430\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435', blank=True)),
                ('resume', models.TextField(null=True, verbose_name='\u0420\u0435\u0437\u044e\u043c\u0435', blank=True)),
                ('columnist', models.CharField(blank=True, max_length=20, null=True, verbose_name='\u0420\u0435\u0446\u0435\u043d\u0437\u0435\u043d\u0442', choices=[(b'siropova', '\u041b\u0438\u0437\u0430 \u0421\u0438\u0440\u043e\u043f\u043e\u0432\u0430'), (b'abram', '\u0410\u0431\u0440\u0430\u043c \u0414\u044e\u0440\u0441\u043e'), (b'buuzin', '\u041c\u0438\u0445\u0430\u0438\u043b \u0411\u0443\u0443\u0437\u0438\u043d'), (b'chesnok', '\u0410\u043d\u0430\u0442\u043e\u043b\u0438\u0439 \u0427\u0435\u0441\u043d\u043e\u043a\u043e\u0432'), (b'olivie', '\u041a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u0438\u043d \u041e\u043b\u0438\u0432\u044c\u0435'), (b'anteater', '\u0410\u0440\u043a\u0430\u0434\u0438\u0439 \u041c\u0443\u0440\u0430\u0432\u044c\u0435\u0434')])),
            ],
            options={
                'verbose_name': '\u043e\u0431\u0437\u043e\u0440',
                'verbose_name_plural': '\u043e\u0431\u0437\u043e\u0440\u044b',
            },
            bases=('obed.article',),
        ),
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('establishment', models.OneToOneField(related_name='_user_rating', primary_key=True, serialize=False, to='obed.Establishment')),
                ('kitchen', models.FloatField(default=0, verbose_name='\u0441\u0440\u0435\u0434\u043d\u044f\u044f \u043e\u0446\u0435\u043d\u043a\u0430 \u043a\u0443\u0445\u043d\u0438')),
                ('service', models.FloatField(default=0, verbose_name='\u0441\u0440\u0435\u0434\u043d\u044f\u044f \u043e\u0446\u0435\u043d\u043a\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u0430')),
                ('environment', models.FloatField(default=0, verbose_name='\u0441\u0440\u0435\u0434\u043d\u044f\u044f \u043e\u0446\u0435\u043d\u043a\u0430 \u043e\u0431\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438')),
                ('total', models.FloatField(default=0, verbose_name='\u0438\u0442\u043e\u0433\u043e\u0432\u0430\u044f \u043e\u0446\u0435\u043d\u043a\u0430')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='\u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0433\u043e\u043b\u043e\u0441\u043e\u0432')),
            ],
            options={
                'db_table': 'obed_user_ratings',
                'verbose_name': '\u0440\u0435\u0439\u0442\u0438\u043d\u0433',
                'verbose_name_plural': '\u0440\u0435\u0439\u0442\u0438\u043d\u0433\u0438',
            },
        ),
        migrations.AddField(
            model_name='promotion',
            name='establishment',
            field=models.ForeignKey(related_name='promotions', verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='obed.Establishment'),
        ),
        migrations.AddField(
            model_name='menuofday',
            name='establishment',
            field=models.ForeignKey(verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='obed.Establishment'),
        ),
        migrations.AddField(
            model_name='menu',
            name='establishment',
            field=models.OneToOneField(related_name='establishment_menu', verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='obed.Establishment'),
        ),
        migrations.AddField(
            model_name='gurucause',
            name='establishments',
            field=models.ManyToManyField(to='obed.Establishment', verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f', blank=True),
        ),
        migrations.AddField(
            model_name='establishment',
            name='main_section',
            field=models.ForeignKey(verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u0440\u0443\u0431\u0440\u0438\u043a\u0430', to='phones.Sections'),
        ),
        migrations.AddField(
            model_name='establishment',
            name='types',
            field=models.ManyToManyField(to='obed.Type', verbose_name='\u0422\u0438\u043f\u044b'),
        ),
        migrations.AddField(
            model_name='corporative',
            name='establishment',
            field=models.OneToOneField(related_name='establishment_corporative', verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='obed.Establishment'),
        ),
        migrations.AddField(
            model_name='award',
            name='establishment',
            field=models.ForeignKey(verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', blank=True, to='obed.Establishment', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='mentions',
            field=models.ManyToManyField(related_name='mentions', verbose_name='\u0423\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u044f', to='obed.Establishment', blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='section_category',
            field=models.ForeignKey(verbose_name='\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f \u0440\u0430\u0437\u0434\u0435\u043b\u0430', to='obed.ArticleCategory'),
        ),
        migrations.AddField(
            model_name='userratinghistory',
            name='rating',
            field=models.ForeignKey(related_name='history', to='obed.UserRating'),
        ),
        migrations.AddField(
            model_name='userratehistory',
            name='rating',
            field=models.ForeignKey(related_name='+', to='obed.UserRating'),
        ),
        migrations.AddField(
            model_name='userrate',
            name='rating',
            field=models.ForeignKey(related_name='rates', to='obed.UserRating'),
        ),
        migrations.AddField(
            model_name='review',
            name='establishment',
            field=models.ForeignKey(verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', blank=True, to='obed.Establishment', null=True),
        ),
        migrations.AddField(
            model_name='establishment',
            name='last_review',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to='obed.Review', null=True, verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u044f\u044f \u0440\u0435\u0446\u0435\u043d\u0437\u0438\u044f'),
        ),
        migrations.AddField(
            model_name='dish',
            name='review',
            field=models.ForeignKey(related_name='review_dishes', verbose_name='\u0420\u0435\u0446\u0435\u043d\u0437\u0438\u044f', to='obed.Review'),
        ),
        migrations.AlterUniqueTogether(
            name='userrate',
            unique_together=set([('user', 'rating')]),
        ),
    ]
