# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_visible', models.BooleanField(default=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f')),
                ('is_operative', models.BooleanField(default=True, verbose_name='\u041c\u043e\u0436\u0435\u0442 \u043f\u0438\u0441\u0430\u0442\u044c')),
                ('subscribers_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a\u043e\u0432')),
                ('entries_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u0441\u0442\u043e\u0432')),
                ('comments_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432 \u043a \u043f\u043e\u0441\u0442\u0430\u043c')),
                ('date_started', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u0437\u0430\u043f\u0438\u0441\u0435\u0439')),
            ],
            options={
                'db_table': 'blogs_authors',
                'verbose_name': '\u0410\u0432\u0442\u043e\u0440',
                'verbose_name_plural': '\u0410\u0432\u0442\u043e\u0440\u044b',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BlogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveIntegerField(default=1, db_index=True, verbose_name='\u0422\u0438\u043f \u0437\u0430\u043f\u0438\u0441\u0438', choices=[(1, '\u0417\u0430\u043f\u0438\u0441\u044c \u0431\u043b\u043e\u0433\u0430'), (2, '\u041a\u043e\u043b\u043e\u043d\u043a\u0430 \u0440\u0435\u0434\u0430\u043a\u0442\u043e\u0440\u0430')])),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('caption', models.TextField(null=True, verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430', blank=True)),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
                ('created', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('updated', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('visible', models.BooleanField(default=False, db_index=True, verbose_name='\u041e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u043d\u043e')),
                ('show_until', models.DateField(null=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0434\u043e', blank=True)),
                ('view_cnt', models.IntegerField(default=0, editable=False)),
                ('comments_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432')),
            ],
            options={
                'db_table': 'blogs_entries',
                'verbose_name': '\u0431\u043b\u043e\u0433',
                'verbose_name_plural': '\u0431\u043b\u043e\u0433\u0438',
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
                ('created', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('updated', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('is_approved', models.BooleanField(default=False, verbose_name='\u041e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u043d\u043e')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d\u043e')),
                ('view_cnt', models.IntegerField(default=0, editable=False)),
                ('comments_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u043e\u0442\u0447\u0435\u0442',
                'verbose_name_plural': '\u043e\u0442\u0447\u0435\u0442\u044b',
            },
        ),
    ]
