# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instagram_id', models.CharField(unique=True, max_length=30)),
                ('is_visible', models.BooleanField(default=True, db_index=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f')),
                ('data', jsonfield.fields.JSONField()),
                ('is_marked', models.BooleanField(default=False, db_index=True, verbose_name='\u0412\u044b\u0434\u0435\u043b\u0435\u043d\u043e')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'externals_instagram_media',
                'verbose_name': 'Instagram',
                'verbose_name_plural': 'Instagram',
            },
        ),
        migrations.CreateModel(
            name='InstagramTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('name', models.CharField(help_text='\u0431\u0435\u0437 #', unique=True, max_length=255, verbose_name='\u0422\u0435\u0433')),
                ('type', models.PositiveIntegerField(default=0, verbose_name='\u0422\u0438\u043f \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u0430', choices=[(0, '\u043b\u044e\u0431\u043e\u0439'), (1, '\u0442\u043e\u043b\u044c\u043a\u043e \u0444\u043e\u0442\u043e'), (2, '\u0442\u043e\u043b\u044c\u043a\u043e \u0432\u0438\u0434\u0435\u043e')])),
                ('is_visible', models.BooleanField(default=True, db_index=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f')),
                ('description', models.TextField(null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('latest_media_id', models.CharField(max_length=30, verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u044b\u0439 id', blank=True)),
                ('site', models.ForeignKey(verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', blank=True, to='options.Site', null=True)),
            ],
            options={
                'db_table': 'externals_instagram_tags',
                'verbose_name': '\u0445\u044d\u0448\u0442\u0435\u0433 Instagram',
                'verbose_name_plural': '\u0445\u044d\u0448\u0442\u0435\u0433\u0438 Instagram',
            },
        ),
        migrations.CreateModel(
            name='InstagramUserBlacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=100, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', db_index=True)),
            ],
            options={
                'verbose_name': '\u0417\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c instagram',
                'verbose_name_plural': '\u0417\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 instagram',
            },
        ),
        migrations.AddField(
            model_name='instagrammedia',
            name='tags',
            field=models.ManyToManyField(related_name='media', verbose_name='\u0445\u044d\u0448\u0442\u0435\u0433 Instagram', to='externals.InstagramTag'),
        ),
    ]
