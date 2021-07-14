# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.newyear2014.models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Congratulation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('sign', models.CharField(max_length=255, null=True, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u044c', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_hidden', models.BooleanField(default=False, verbose_name='\u0421\u043a\u0440\u044b\u0442\u043e\u0435')),
            ],
            options={
                'verbose_name': '\u043f\u043e\u0437\u0434\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u043f\u043e\u0437\u0434\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='GuruAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('gender', models.CharField(db_index=True, max_length=1, verbose_name='\u041f\u043e\u043b', choices=[(b'm', '\u043c\u0443\u0436\u0441\u043a\u043e\u0439'), (b'f', '\u0436\u0435\u043d\u0441\u043a\u0438\u0439')])),
                ('age', models.CharField(db_index=True, max_length=10, verbose_name='\u0412\u043e\u0437\u0440\u0430\u0441\u0442', choices=[(b'lt30', '\u043c\u043b\u0430\u0434\u0448\u0435 30'), (b'gt30', '\u0441\u0442\u0430\u0440\u0448\u0435 30')])),
            ],
            options={
                'verbose_name': '\u043e\u0442\u0432\u0435\u0442 \u043a\u0430\u043a \u0432\u0441\u0442\u0440\u0435\u0442\u0438\u0442\u044c \u041d\u0413',
                'verbose_name_plural': '\u043e\u0442\u0432\u0435\u0442\u044b \u043a\u0430\u043a \u0432\u0441\u0442\u0440\u0435\u0442\u0438\u0442\u044c \u041d\u0413',
            },
        ),
        migrations.CreateModel(
            name='Horoscope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('short_name', models.CharField(max_length=255, null=True, verbose_name='\u041a\u043e\u0440\u043e\u0442\u043a\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
            ],
            options={
                'verbose_name': '\u0433\u043e\u0440\u043e\u0441\u043a\u043e\u043f',
                'verbose_name_plural': '\u0433\u043e\u0440\u043e\u0441\u043a\u043e\u043f\u044b',
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_start', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('date_end', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u043e\u043a\u0430\u0437\u0430', db_index=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('caption', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430')),
                ('content', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.newyear2014.models.offer_image_upload_to, verbose_name='\u0424\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('url', models.URLField(null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True)),
            ],
            options={
                'verbose_name': '\u043b\u0443\u0447\u0448\u0435\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u043b\u0443\u0447\u0448\u0438\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='PhotoContest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('caption', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430')),
                ('content', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.newyear2014.models.contest_image_upload_to, verbose_name='\u0424\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('date_start', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f', db_index=True)),
                ('date_end', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f', db_index=True)),
                ('sponsor_title', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u043f\u043e\u043d\u0441\u043e\u0440\u0430', blank=True)),
                ('sponsor_image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.newyear2014.models.contest_sponsor_upload_to, null=True, verbose_name='\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430 \u0441\u043f\u043e\u043d\u0441\u043e\u0440\u0430', blank=True)),
                ('is_blocked', models.BooleanField(default=False, help_text='\u0413\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f, \u043d\u043e \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u043f\u0440\u043e\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u0442\u044c \u043e\u0442\u043a\u043b\u044e\u0447\u0435\u043d\u0430', verbose_name='\u0417\u0430\u043a\u0440\u044b\u0442\u044c \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('user_can_add', models.BooleanField(default=True, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 \u043c\u043e\u0433\u0443\u0442 \u0434\u043e\u0431\u0430\u0432\u043b\u044f\u0442\u044c\u0441\u044f')),
            ],
            options={
                'verbose_name': '\u0444\u043e\u0442\u043e\u043a\u043e\u043d\u043a\u0443\u0440\u0441',
                'verbose_name_plural': '\u0444\u043e\u0442\u043e\u043a\u043e\u043d\u043a\u0443\u0440\u0441\u044b',
            },
        ),
        migrations.CreateModel(
            name='PhotoContestParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_visible', models.BooleanField(default=True, db_index=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f')),
                ('name', models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.newyear2014.models.contest_participant_image_upload_to)),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
            ],
            options={
                'verbose_name': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a \u0444\u043e\u0442\u043e\u043a\u043e\u043d\u043a\u0443\u0440\u0441\u0430',
                'verbose_name_plural': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u0438 \u0444\u043e\u0442\u043e\u043a\u043e\u043d\u043a\u0443\u0440\u0441\u0430',
            },
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=255, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
            ],
            options={
                'verbose_name': '\u043e\u0442\u0432\u0435\u0442 \u0434\u043b\u044f \u0433\u0430\u0434\u0430\u043d\u0438\u044f',
                'verbose_name_plural': '\u043e\u0442\u0432\u0435\u0442\u044b \u0434\u043b\u044f \u0433\u0430\u0434\u0430\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Puzzle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.newyear2014.models.wallpaper_image_upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('url', models.CharField(help_text='\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: /news/photo/20130917/holiday/#event=312990', max_length=100, null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0444\u043e\u0442\u043e \u0432 \u0444\u043e\u0442\u043e\u0440\u0435\u043f\u043e\u0440\u0442\u0430\u0436\u0435', blank=True)),
            ],
            options={
                'verbose_name': '\u043f\u0430\u0437\u043b',
                'verbose_name_plural': '\u043f\u0430\u0437\u043b\u044b',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '\u0432\u043e\u043f\u0440\u043e\u0441 \u043a \u0433\u0430\u0434\u0430\u043d\u0438\u044e',
                'verbose_name_plural': '\u0432\u043e\u043f\u0440\u043e\u0441\u044b \u043a \u0433\u0430\u0434\u0430\u043d\u0438\u044e',
            },
        ),
        migrations.CreateModel(
            name='TextContest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('caption', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430')),
                ('content', models.TextField(verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.newyear2014.models.contest_image_upload_to, verbose_name='\u0424\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('date_start', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430 \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f', db_index=True)),
                ('date_end', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u0440\u043e\u0432\u0435\u0434\u0435\u043d\u0438\u044f', db_index=True)),
                ('sponsor_title', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u043f\u043e\u043d\u0441\u043e\u0440\u0430', blank=True)),
                ('sponsor_image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.newyear2014.models.contest_sponsor_upload_to, null=True, verbose_name='\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430 \u0441\u043f\u043e\u043d\u0441\u043e\u0440\u0430', blank=True)),
                ('is_blocked', models.BooleanField(default=False, help_text='\u0413\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f, \u043d\u043e \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u043f\u0440\u043e\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u0442\u044c \u043e\u0442\u043a\u043b\u044e\u0447\u0435\u043d\u0430', verbose_name='\u0417\u0430\u043a\u0440\u044b\u0442\u044c \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('user_can_add', models.BooleanField(default=True, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 \u043c\u043e\u0433\u0443\u0442 \u0434\u043e\u0431\u0430\u0432\u043b\u044f\u0442\u044c\u0441\u044f')),
            ],
            options={
                'verbose_name': '\u0442\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0439 \u043a\u043e\u043d\u043a\u0443\u0440\u0441',
                'verbose_name_plural': '\u0442\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0435 \u043a\u043e\u043d\u043a\u0443\u0440\u0441\u044b',
            },
        ),
        migrations.CreateModel(
            name='TextContestParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_visible', models.BooleanField(default=True, db_index=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u0442\u0441\u044f')),
                ('name', models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
            ],
            options={
                'verbose_name': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a \u0442\u0435\u043a\u0441\u0442\u043e\u0432\u043e\u0433\u043e \u043a\u043e\u043d\u043a\u0443\u0440\u0441\u0430',
                'verbose_name_plural': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u0438 \u0442\u0435\u043a\u0441\u0442\u043e\u0432\u043e\u0433\u043e \u043a\u043e\u043d\u043a\u0443\u0440\u0441\u0430',
            },
        ),
        migrations.CreateModel(
            name='Wallpaper',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('standard_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u043e\u043c 1280x1024', upload_to=irk.newyear2014.models.wallpaper_image_upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('wide_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0440\u0430\u0437\u043c\u0435\u0440\u043e\u043c 1920x1080', upload_to=irk.newyear2014.models.wallpaper_image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u043e\u0435 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
            ],
            options={
                'verbose_name': '\u043e\u0431\u043e\u0438',
                'verbose_name_plural': '\u043e\u0431\u043e\u0438',
            },
        ),
        migrations.CreateModel(
            name='Wish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '\u0436\u0435\u043b\u0430\u043d\u0438\u0435',
                'verbose_name_plural': '\u0436\u0435\u043b\u0430\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Zodiac',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/newyear2014/horoscope/', verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
            ],
            options={
                'verbose_name': '\u0437\u043d\u0430\u043a \u0437\u043e\u0434\u0438\u0430\u043a\u0430',
                'verbose_name_plural': '\u0437\u043d\u0430\u043a\u0438 \u0437\u043e\u0434\u0438\u0430\u043a\u0430',
            },
        ),
    ]
