# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.contrib.auth.models
import irk.profiles.models
from django.conf import settings
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Counter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.PositiveIntegerField()),
                ('state', models.PositiveIntegerField(null=True, blank=True)),
                ('model', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('param', models.CharField(max_length=100)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_banned', models.BooleanField(default=False, verbose_name='\u0417\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d')),
                ('is_closed', models.BooleanField(default=False, verbose_name='\u0417\u0430\u043a\u0440\u044b\u0442')),
                ('bann_end', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430, \u0434\u043e \u043a\u043e\u0442\u043e\u0440\u043e\u0439 \u0437\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d', blank=True)),
                ('hash', models.CharField(max_length=40, editable=False)),
                ('hash_stamp', models.DateTimeField(default=datetime.datetime.now, null=True, editable=False, blank=True)),
                ('is_moderator', models.BooleanField(default=False)),
                ('mname', models.CharField(max_length=100, verbose_name='\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e', blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, verbose_name='\u041f\u043e\u043b', choices=[(b'm', '\u043c\u0443\u0436\u0441\u043a\u043e\u0439'), (b'f', '\u0436\u0435\u043d\u0441\u043a\u0438\u0439')])),
                ('address', models.CharField(max_length=255, verbose_name='\u0410\u0434\u0440\u0435\u0441', blank=True)),
                ('phone', models.CharField(max_length=20, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d', blank=True)),
                ('birthday', models.DateField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f', blank=True)),
                ('subscribe', models.BooleanField(default=False, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043d\u0430 \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0443 \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439')),
                ('comments_notify', models.BooleanField(default=True, verbose_name='\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u044f\u0442\u044c \u043e\u0431 \u043e\u0442\u0432\u0435\u0442\u0430\u0445 \u043d\u0430 \u043c\u043e\u0438 \u043e\u0442\u0437\u044b\u0432\u044b')),
                ('session_id', models.CharField(max_length=32, editable=False)),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.profiles.models.get_user_image_path, verbose_name='\u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('rating_votes_cnt', models.IntegerField(default=10, help_text='\u0414\u043b\u044f \u0440\u0435\u0439\u0442\u0438\u043d\u0433\u043e\u0432 \u0437\u0430\u0434\u0430\u0447', verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0433\u043e\u043b\u043e\u0441\u043e\u0432', editable=False)),
                ('signature', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u044c', blank=True)),
                ('is_verified', models.BooleanField(default=False, verbose_name='\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', editable=False)),
                ('full_name', models.CharField(max_length=100, verbose_name='\u0418\u043c\u044f')),
                ('type', models.PositiveSmallIntegerField(default=0, verbose_name='\u0422\u0438\u043f', choices=[(0, '\u043b\u0438\u0447\u043d\u044b\u0439'), (1, '\u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u043d\u044b\u0439')])),
                ('company_name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438', blank=True)),
            ],
            options={
                'verbose_name': '\u043f\u0440\u043e\u0444\u0438\u043b\u044c',
                'verbose_name_plural': '\u043f\u0440\u043e\u0444\u0438\u043b\u044c',
                'permissions': (('can_ban_profile', 'Can ban profile'),),
            },
        ),
        migrations.CreateModel(
            name='ProfileSocial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveSmallIntegerField(verbose_name='\u0422\u0438\u043f', choices=[(0, '\u0412\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0435'), (1, '\u041e\u0434\u043d\u043e\u043a\u043b\u0430\u0441\u0441\u043d\u0438\u043a\u0438'), (2, '\u0422\u0432\u0438\u0442\u0442\u0435\u0440'), (3, '\u0424\u0435\u0439\u0441\u0431\u0443\u043a'), (4, 'Instagram')])),
                ('url', models.URLField(verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430')),
                ('profile', models.ForeignKey(related_name='social', to='profiles.Profile')),
            ],
            options={
                'db_table': 'profiles_social',
                'verbose_name': '\u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0435\u0442\u044c',
                'verbose_name_plural': '\u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0435 \u0441\u0435\u0442\u0438',
            },
        ),
        migrations.CreateModel(
            name='UserBanHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.TextField(blank=True)),
                ('created', models.DateTimeField()),
                ('ended', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'verbose_name': '\u0438\u0441\u0442\u043e\u0440\u0438\u044f \u0431\u0430\u043d\u043e\u0432 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
                'verbose_name_plural': '\u0438\u0441\u0442\u043e\u0440\u0438\u044f \u0431\u0430\u043d\u043e\u0432 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
            },
        ),
        migrations.CreateModel(
            name='ProfileGroup',
            fields=[
            ],
            options={
                'verbose_name': '\u0433\u0440\u0443\u043f\u043fe',
                'proxy': True,
                'verbose_name_plural': '\u0433\u0440\u0443\u043f\u043f\u044b',
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='ProfileUser',
            fields=[
            ],
            options={
                'verbose_name': '\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c',
                'proxy': True,
                'verbose_name_plural': '\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='userbanhistory',
            name='moderator',
            field=models.ForeignKey(related_name='banned', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userbanhistory',
            name='user',
            field=models.ForeignKey(related_name='bans', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='options',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='counter',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CorporativeProfile',
            fields=[
            ],
            options={
                'verbose_name': '\u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u043d\u044b\u0439 \u0430\u043a\u043a\u0430\u0443\u043d\u0442',
                'proxy': True,
                'verbose_name_plural': '\u043a\u043e\u0440\u043f\u043e\u0440\u0430\u0442\u0438\u0432\u043d\u044b\u0435 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u044b',
            },
            bases=('profiles.profile',),
        ),
        migrations.CreateModel(
            name='ProfileBannedUser',
            fields=[
            ],
            options={
                'verbose_name': '\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c (\u0431\u0430\u043d)',
                'proxy': True,
                'verbose_name_plural': '\u0431\u0430\u043d \u043b\u0438\u0441\u0442 \u043b\u043e\u0433\u0438\u043d\u043e\u0432',
            },
            bases=('profiles.profile',),
        ),
    ]
