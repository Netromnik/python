# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.news.models
from django.conf import settings
import irk.contests.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('image', models.ImageField(upload_to=irk.contests.models.textblock_upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('image_caption', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f', blank=True)),
                ('w_image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('date_start', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', db_index=True)),
                ('date_end', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043a\u043e\u043d\u0446\u0430', db_index=True)),
                ('is_blocked', models.BooleanField(default=False, help_text='\u0413\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f, \u043d\u043e \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u043f\u0440\u043e\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u0442\u044c \u043e\u0442\u043a\u043b\u044e\u0447\u0435\u043d\u0430', verbose_name='\u0417\u0430\u043a\u0440\u044b\u0442\u044c \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('type', models.CharField(default=b'photo', max_length=10, verbose_name='\u0422\u0438\u043f', db_index=True, choices=[(b'photo', '\u041f\u043e\u043a\u0430\u0437\u0443\u0445\u0430'), (b'quiz', '\u0412\u0438\u043a\u0442\u043e\u0440\u0438\u043d\u0430')])),
                ('vote_type', models.SmallIntegerField(default=2, verbose_name='\u0413\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435', choices=[(1, '\u0447\u0435\u0440\u0435\u0437 \u0441\u043c\u0441'), (2, '\u043d\u0430 \u0441\u0430\u0439\u0442\u0435')])),
                ('user_can_add', models.BooleanField(default=True, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 \u043c\u043e\u0433\u0443\u0442 \u0434\u043e\u0431\u0430\u0432\u043b\u044f\u0442\u044c\u0441\u044f')),
                ('instagram_tag', models.CharField(max_length=50, verbose_name='\u0425\u044d\u0448\u0442\u0435\u0433 Instagram', blank=True)),
            ],
            options={
                'db_table': 'contests_contests',
                'verbose_name': '\u043a\u043e\u043d\u043a\u0443\u0440\u0441',
                'verbose_name_plural': '\u043a\u043e\u043d\u043a\u0443\u0440\u0441\u044b',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('description', models.TextField(default=b'', verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('comments_cnt', models.PositiveIntegerField(default=0, editable=False)),
                ('sms_value', models.IntegerField(null=True, verbose_name='\u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u0441\u043c\u0441 \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u044f', blank=True)),
                ('sms_code', models.CharField(max_length=255, null=True, verbose_name='\u041a\u043e\u0434 \u0434\u043b\u044f \u0441\u043c\u0441', blank=True)),
                ('username', models.CharField(max_length=100, null=True, verbose_name='\u0418\u043c\u044f', blank=True)),
                ('instagram_id', models.CharField(verbose_name='Instagram ID', max_length=40, null=True, editable=False, blank=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043d\u0430 \u0441\u0430\u0439\u0442\u0435')),
                ('full_name', models.CharField(max_length=100, verbose_name='\u0438\u043c\u044f \u0438 \u0444\u0430\u043c\u0438\u043b\u0438\u044f', blank=True)),
                ('phone', models.CharField(max_length=20, verbose_name='\u0442\u0435\u043b\u0435\u0444\u043e\u043d', blank=True)),
                ('contest', models.ForeignKey(related_name='participants', verbose_name='\u041a\u043e\u043d\u043a\u0443\u0440\u0441', to='contests.Contest')),
                ('user', models.ForeignKey(verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'contests_competitors',
                'verbose_name': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a',
                'verbose_name_plural': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u0438',
            },
        ),
    ]
