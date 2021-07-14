# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file
import irk.utils.db.models.fields.color
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('description', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('color', irk.utils.db.models.fields.color.ColorField(help_text='\u0412 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 #13bf99', max_length=6, verbose_name='\u0426\u0432\u0435\u0442')),
                ('branding', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440\u044b \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f: 1920\xd7600 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/special/branding', null=True, verbose_name='\u0411\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('html_head', models.TextField(verbose_name='HTML \u043f\u043e\u0434 \u0448\u0430\u043f\u043a\u043e\u0439', blank=True)),
                ('image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/special/project', verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('show_on_home', models.BooleanField(default=False, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0432 \u0431\u043b\u043e\u043a\u0435 \u0421\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432 \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')),
                ('icon', irk.utils.fields.file.FileRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f: 31x31', upload_to=b'img/site/news/subject/icon', null=True, verbose_name='\u0438\u043a\u043e\u043d\u043a\u0430 \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 SVG', blank=True)),
                ('site', models.ForeignKey(related_name='project', verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', to='options.Site')),
            ],
            options={
                'verbose_name': '\u0421\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442',
                'verbose_name_plural': '\u0421\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442\u044b',
            },
        ),
    ]
