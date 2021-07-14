# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('experts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('phones', '0001_initial'),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expert',
            name='firm',
            field=models.ForeignKey(verbose_name='\u041e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u044f', blank=True, to='phones.Firms', null=True),
        ),
        migrations.AddField(
            model_name='expert',
            name='person',
            field=models.ForeignKey(verbose_name='\u041f\u0435\u0440\u0441\u043e\u043d\u0430', blank=True, to='news.Person', null=True),
        ),
        migrations.AddField(
            model_name='expert',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
