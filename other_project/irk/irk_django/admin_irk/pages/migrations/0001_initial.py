# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('file', irk.utils.fields.file.FileRemovableField(upload_to=b'img/site/pages/', verbose_name='\u0424\u0430\u0439\u043b')),
                ('href', models.CharField(max_length=100, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': '\u0424\u0430\u0439\u043b\u044b',
                'verbose_name_plural': '\u0424\u0430\u0439\u043b\u044b',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=100, verbose_name='URL', db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='title', blank=True)),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('sub_content', models.TextField(verbose_name='\u0414\u043e\u043f. \u043a\u043e\u043d\u0442\u0435\u043d\u0442', blank=True)),
                ('template_name', models.CharField(max_length=70, verbose_name='template name', blank=True)),
                ('position', models.IntegerField(default=0, db_index=True, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', blank=True)),
                ('editors', models.ManyToManyField(to='auth.Group', verbose_name='\u0420\u0435\u0434\u0430\u043a\u0442\u043e\u0440\u044b')),
                ('site', models.ForeignKey(verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', to='options.Site')),
            ],
            options={
                'ordering': ('position', 'title'),
                'verbose_name': '\u043f\u0440\u043e\u0441\u0442\u0430\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430',
                'verbose_name_plural': '\u043f\u0440\u043e\u0441\u0442\u044b\u0435 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b',
            },
        ),
        migrations.AddField(
            model_name='file',
            name='flatpage',
            field=models.ForeignKey(to='pages.Page'),
        ),
    ]
