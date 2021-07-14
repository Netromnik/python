# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.news.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0017_socialpult'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialPultUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=irk.news.models.social_pult_upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('material', models.ForeignKey(related_name='social_pult_uploads', on_delete=django.db.models.deletion.SET_NULL, to='news.BaseMaterial', null=True)),
            ],
        ),
    ]
