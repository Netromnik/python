# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.db.models.fields.color
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('url', models.CharField(max_length=255, verbose_name='URL', blank=True)),
                ('slugs', models.CharField(unique=True, max_length=50, verbose_name='\u0410\u043b\u0438\u0430\u0441\u044b')),
                ('position', models.IntegerField(verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('menu_class', models.CharField(max_length=15, verbose_name='\u041a\u043b\u0430\u0441\u0441', blank=True)),
                ('in_menu', models.BooleanField(default=False, help_text='\u0415\u0441\u043b\u0438 \u0433\u0430\u043b\u043e\u0447\u043a\u0430 \u0441\u0442\u043e\u0438\u0442, \u0442\u043e \u0431\u0443\u0434\u0435\u0442 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c\u0441\u044f \u0432 \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u043c \u043c\u0435\u043d\u044e, \u0435\u0441\u043b\u0438 \u043d\u0435\u0442 \u0442\u043e \u0432 \u0441\u043f\u0438\u0441\u043a\u0435 "\u0435\u0449\u0451"', verbose_name='\u0412 \u043c\u0435\u043d\u044e')),
                ('is_hidden', models.BooleanField(default=False, help_text='\u041d\u0435 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f \u0432 \u043c\u0435\u043d\u044e \u0432\u043e\u043e\u0431\u0449\u0435', db_index=True, verbose_name='\u0421\u043f\u0440\u044f\u0442\u0430\u043d')),
                ('booking_visible', models.BooleanField(default=False, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u0432 \u0430\u0434\u0440\u0435\u0441\u043a\u0435')),
                ('mark_in_menu', models.BooleanField(default=False, verbose_name='\u0412 \u0432\u0435\u0440\u0445\u043d\u0435\u0439 \u0441\u0442\u0440\u043e\u043a\u0435')),
                ('highlight', models.BooleanField(default=False, verbose_name='\u041f\u043e\u0434\u0441\u0432\u0435\u0447\u0438\u0432\u0430\u0442\u044c')),
                ('small', models.BooleanField(default=False, verbose_name='\u0423\u043c\u0435\u043d\u044c\u0448\u0435\u043d\u043d\u0430\u044f \u0448\u0430\u043f\u043a\u0430')),
                ('blogs_through_perms', models.BooleanField(default=False, verbose_name='\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435/\u0440\u0435\u0434. \u0431\u043b\u043e\u0433\u043e\u0432 \u0442\u043e\u043b\u044c\u043a\u043e \u0447\u0435\u0440\u0435\u0437 \u043f\u0440\u0430\u0432\u0430.')),
                ('show_in_bar', models.BooleanField(default=False, help_text='\u0414\u043b\u044f \u0432\u043d\u0435\u0448\u043d\u0438\u0445 \u0441\u0430\u0439\u0442\u043e\u0432', verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0432 \u043f\u043e\u043b\u043e\u0441\u0435 \u043d\u0430\u0432\u0438\u0433\u0430\u0446\u0438\u0438')),
                ('track_transition', models.BooleanField(default=False, help_text='\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0445\u0440\u0430\u043d\u0438\u0442\u0441\u044f \u0432 Google.Analytics', verbose_name='\u041f\u043e\u0434\u0441\u0447\u0438\u0442\u044b\u0432\u0430\u0442\u044c \u043f\u0435\u0440\u0435\u0445\u043e\u0434\u044b')),
                ('icon', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/option/icon/', null=True, verbose_name='\u0418\u043a\u043e\u043d\u043a\u0430', blank=True)),
                ('show_icon', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0438\u043a\u043e\u043d\u043a\u0443')),
                ('branding_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440\u044b \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f: 1920\xd7250 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/adv/branding', null=True, verbose_name='\u0411\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('branding_color', irk.utils.db.models.fields.color.ColorField(help_text='\u0412 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 #13bf99', max_length=6, null=True, verbose_name='\u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430 \u0431\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f', blank=True)),
                ('widget_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f \u0441\u043f\u0440\u0430\u0432\u0430 \u043e\u0442 \u043c\u0435\u043d\u044e', upload_to=b'img/site/adv/widgets', null=True, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0432\u0438\u0434\u0436\u0435\u0442\u0430', blank=True)),
                ('widget_link', models.URLField(null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u0432\u0438\u0434\u0436\u0435\u0442\u0430', blank=True)),
                ('widget_text', models.CharField(max_length=255, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442 \u0432\u0438\u0434\u0436\u0435\u0442\u0430', blank=True)),
            ],
            options={
                'ordering': ['position'],
                'db_table': 'options_site',
                'verbose_name': '\u0440\u0430\u0437\u0434\u0435\u043b',
                'verbose_name_plural': '\u0440\u0430\u0437\u0434\u0435\u043b\u044b',
            },
        ),
    ]
