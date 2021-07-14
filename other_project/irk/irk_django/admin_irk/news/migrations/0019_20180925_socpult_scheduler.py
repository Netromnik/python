# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.news.models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0001_20180925_socpult_scheduler'),
        ('news', '0018_socialpultupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialpost',
            name='scheduled_task',
            field=models.ForeignKey(to='scheduler.Task', null=True),
        ),
        migrations.AddField(
            model_name='socialpultupload',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='\u0421\u043e\u0437\u0434\u0430\u043d\u043e', null=True),
        ),
        migrations.AlterField(
            model_name='socialpost',
            name='social_pult_post',
            field=models.ForeignKey(related_name='social_posts', to='news.SocialPultPost', null=True),
        ),
        migrations.AlterField(
            model_name='socialpultupload',
            name='image',
            field=irk.utils.fields.file.FileRemovableField(upload_to=irk.news.models.social_pult_upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0438\u043b\u0438 \u0432\u0438\u0434\u0435\u043e'),
        ),
    ]
