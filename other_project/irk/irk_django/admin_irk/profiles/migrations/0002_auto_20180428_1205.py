# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='full_name',
            field=models.CharField(max_length=100, verbose_name='\u0412\u0438\u0434\u0438\u043c\u043e\u0435 \u0438\u043c\u044f'),
        ),
        migrations.AlterField(
            model_name='userbanhistory',
            name='moderator',
            field=models.ForeignKey(related_name='banned', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
