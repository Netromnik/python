# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.news.models
import datetime
import irk.utils.fields.file
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Magazine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('social_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 940x445', upload_to=irk.news.models.social_card_upload_to, null=True, verbose_name='\u0424\u043e\u043d \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('social_text', models.CharField(help_text='100 \u0437\u043d\u0430\u043a\u043e\u0432', max_length=100, verbose_name='\u0422\u0435\u043a\u0441\u0442 \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('social_label', models.CharField(help_text='50 \u0437\u043d\u0430\u043a\u043e\u0432', max_length=50, verbose_name='\u041c\u0435\u0442\u043a\u0430', blank=True)),
                ('social_card', models.ImageField(upload_to=irk.news.models.social_card_upload_to, null=True, verbose_name='\u041a\u0430\u0440\u0442\u043e\u0447\u043a\u0430 \u0434\u043b\u044f \u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0445 \u0441\u0435\u0442\u0435\u0439', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('caption', models.TextField(default='', verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430')),
                ('slug', models.SlugField(verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('visible', models.BooleanField(default=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043d\u0430 \u0441\u0430\u0439\u0442\u0435')),
                ('show_on_home', models.BooleanField(default=False, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('home_image', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/magazine/', null=True, verbose_name='\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0434\u043b\u044f \u0433\u043b\u0430\u0432\u043d\u043e\u0439', blank=True)),
            ],
            options={
                'verbose_name': '\u0436\u0443\u0440\u043d\u0430\u043b',
                'verbose_name_plural': '\u0436\u0443\u0440\u043d\u0430\u043b\u044b',
            },
        ),
        migrations.CreateModel(
            name='MagazineAuthor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/magazine/author', null=True, verbose_name='\u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('position', models.CharField(default='', max_length=255, verbose_name='\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c', blank=True)),
            ],
            options={
                'verbose_name': '\u0430\u0432\u0442\u043e\u0440 \u0436\u0443\u0440\u043d\u0430\u043b\u0430',
                'verbose_name_plural': '\u0430\u0432\u0442\u043e\u0440\u044b \u0436\u0443\u0440\u043d\u0430\u043b\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='MagazineSubscriber',
            fields=[
                ('email', models.EmailField(max_length=40, serialize=False, verbose_name='E-mail', primary_key=True)),
                ('hash', models.CharField(max_length=40, editable=False)),
                ('is_active', models.BooleanField(default=True, db_index=True, verbose_name='\u0410\u043a\u0442\u0438\u0432\u0438\u0440\u043e\u0432\u0430\u043d')),
                ('hash_stamp', models.DateTimeField(default=datetime.datetime.now, null=True, editable=False, blank=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a \u0436\u0443\u0440\u043d\u0430\u043b\u0430',
                'verbose_name_plural': '\u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a\u0438 \u0436\u0443\u0440\u043d\u0430\u043b\u0430',
            },
        ),
        migrations.AddField(
            model_name='magazine',
            name='caption_author',
            field=models.ForeignKey(verbose_name='\u0410\u0432\u0442\u043e\u0440 \u043f\u043e\u0434\u0432\u043e\u0434\u043a\u0438', blank=True, to='magazine.MagazineAuthor', null=True),
        ),
    ]
