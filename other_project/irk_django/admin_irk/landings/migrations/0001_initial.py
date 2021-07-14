# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f')),
                ('contact', models.CharField(max_length=255, verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b')),
                ('attach', irk.utils.fields.file.FileRemovableField(upload_to='img/site/landings/attach/', null=True, verbose_name='\u041f\u0440\u0438\u043a\u0440\u0435\u043f\u043b\u0435\u043d\u043d\u044b\u0439 \u0444\u0430\u0439\u043b', blank=True)),
                ('link', models.CharField(default='', max_length=255, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0440\u0435\u0437\u044e\u043c\u0435', blank=True)),
                ('content', models.TextField(default='', verbose_name='\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0440\u0435\u0437\u044e\u043c\u0435',
                'verbose_name_plural': '\u0440\u0435\u0437\u044e\u043c\u0435',
            },
        ),
    ]
