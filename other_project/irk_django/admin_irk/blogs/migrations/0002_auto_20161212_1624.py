# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial'),
        ('options', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='site',
            field=models.ForeignKey(related_name='blog_entries', verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', blank=True, to='options.Site', null=True),
        ),
        migrations.AddField(
            model_name='blogentry',
            name='author',
            field=models.ForeignKey(related_name='entries', to='blogs.Author'),
        ),
        migrations.AddField(
            model_name='blogentry',
            name='site',
            field=models.ForeignKey(verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', blank=True, to='options.Site', null=True),
        ),
        migrations.CreateModel(
            name='AdminBlogEntry',
            fields=[
            ],
            options={
                'verbose_name': '\u043a\u043e\u043b\u043e\u043d\u043a\u0430 \u0440\u0435\u0434\u0430\u043a\u0442\u043e\u0440\u0430',
                'proxy': True,
                'verbose_name_plural': '\u043a\u043e\u043b\u043e\u043d\u043a\u0438 \u0440\u0435\u0434\u0430\u043a\u0442\u043e\u0440\u043e\u0432',
            },
            bases=('blogs.blogentry',),
        ),
        migrations.CreateModel(
            name='UserBlogEntry',
            fields=[
            ],
            options={
                'verbose_name': '\u0431\u043b\u043e\u0433',
                'proxy': True,
                'verbose_name_plural': '\u0431\u043b\u043e\u0433\u0438',
            },
            bases=('blogs.blogentry',),
        ),
    ]
