# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0016_auto_20180507_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'', max_length=50, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441 \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438')),
                ('task_id', models.CharField(default=b'', max_length=100, verbose_name='ID \u0432 celery')),
                ('network', models.CharField(max_length=250, verbose_name='\u0421\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0435\u0442\u044c')),
                ('response', models.CharField(default=b'', max_length=2000, verbose_name='\u041e\u0442\u0432\u0435\u0442 \u0441\u043e\u0446\u0441\u0435\u0442\u0438 (json)')),
                ('error', models.CharField(default=b'', max_length=2000, verbose_name='\u041e\u0448\u0438\u0431\u043a\u0430')),
                ('link', models.CharField(default=b'', max_length=250, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
            ],
        ),
        migrations.CreateModel(
            name='SocialPultDraft',
            fields=[
                ('material', models.OneToOneField(related_name='social_pult_draft', primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('data', models.TextField(default=b'', verbose_name='\u0414\u0430\u043d\u043d\u044b\u0435 \u0440\u0435\u0434\u0430\u043a\u0442\u043e\u0440\u0430', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SocialPultPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(default=b'', max_length=10000, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_twitter', models.CharField(default=b'', max_length=500, verbose_name='\u0422\u0435\u043a\u0441\u0442 \u0434\u043b\u044f \u0442\u0432\u0438\u0442\u0442\u0435\u0440\u0430')),
                ('url', models.CharField(default=b'', max_length=500, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430')),
                ('selected_images', models.CharField(default=b'', max_length=1000, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f (json)')),
                ('material', models.ForeignKey(related_name='social_pult_post', to='news.BaseMaterial')),
            ],
        ),
        migrations.AddField(
            model_name='socialpost',
            name='material',
            field=models.ForeignKey(to='news.BaseMaterial'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='social_pult_post',
            field=models.ForeignKey(related_name='social_posts', on_delete=django.db.models.deletion.SET_NULL, to='news.SocialPultPost', null=True),
        ),
    ]
