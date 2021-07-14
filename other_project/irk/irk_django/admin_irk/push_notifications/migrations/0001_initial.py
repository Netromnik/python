# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registration_id', models.CharField(max_length=300, verbose_name='\u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440')),
                ('driver', models.PositiveSmallIntegerField(verbose_name='\u0442\u0440\u0430\u043d\u0441\u043f\u043e\u0440\u0442', choices=[(1, b'google'), (2, b'firefox')])),
                ('is_active', models.BooleanField(default=True, db_index=True, verbose_name='\u0430\u043a\u0442\u0438\u0432\u0435\u043d')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u043c\u043e\u0434\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u043d')),
                ('user', models.ForeignKey(verbose_name='\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e',
                'verbose_name_plural': '\u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430',
            },
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.PositiveSmallIntegerField(default=1, db_index=True, verbose_name='\u0441\u0442\u0430\u0442\u0443\u0441', choices=[(1, '\u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e'), (2, '\u043f\u043e\u043b\u0443\u0447\u0435\u043d\u043e')])),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u0430')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u043c\u043e\u0434\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u0430')),
                ('device', models.ForeignKey(verbose_name='\u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e \u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a\u0430', to='push_notifications.Device')),
            ],
            options={
                'verbose_name': '\u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0430',
                'verbose_name_plural': '\u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('text', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442')),
                ('link', models.URLField(verbose_name='\u0441\u0441\u044b\u043b\u043a\u0430', blank=True)),
                ('alias', models.CharField(db_index=True, max_length=50, verbose_name='\u0430\u043b\u0438\u0430\u0441', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('sent', models.DateTimeField(verbose_name='\u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e', null=True, editable=False)),
                ('devices', models.ManyToManyField(related_name='messages', through='push_notifications.Distribution', to='push_notifications.Device')),
            ],
            options={
                'verbose_name': '\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.AddField(
            model_name='distribution',
            name='message',
            field=models.ForeignKey(verbose_name='\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435', to='push_notifications.Message'),
        ),
        migrations.AlterUniqueTogether(
            name='distribution',
            unique_together=set([('device', 'message')]),
        ),
    ]
