# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.news.models
import datetime
import irk.utils.fields.file
import irk.utils.fields.file
import irk.utils.helpers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('social_label', models.CharField(max_length=255, verbose_name='\u041c\u0435\u0442\u043a\u0430 \u0434\u043b\u044f \u0441\u043e\u0446\u0438\u043e\u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'db_table': 'news_article_types',
                'verbose_name': '\u0422\u0438\u043f \u0441\u0442\u0430\u0442\u0435\u0439',
                'verbose_name_plural': '\u0422\u0438\u043f\u044b \u0441\u0442\u0430\u0442\u0435\u0439',
            },
        ),
        migrations.CreateModel(
            name='BaseMaterial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('social_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 940x445', upload_to=irk.news.models.social_card_upload_to, null=True, verbose_name='\u0424\u043e\u043d \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('social_text', models.CharField(help_text='100 \u0437\u043d\u0430\u043a\u043e\u0432', max_length=100, verbose_name='\u0422\u0435\u043a\u0441\u0442 \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('social_label', models.CharField(help_text='50 \u0437\u043d\u0430\u043a\u043e\u0432', max_length=50, verbose_name='\u041c\u0435\u0442\u043a\u0430', blank=True)),
                ('social_card', models.ImageField(upload_to=irk.news.models.social_card_upload_to, null=True, verbose_name='\u041a\u0430\u0440\u0442\u043e\u0447\u043a\u0430 \u0434\u043b\u044f \u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0445 \u0441\u0435\u0442\u0435\u0439', blank=True)),
                ('stamp', models.DateField(verbose_name='\u0414\u0430\u0442\u0430', db_index=True)),
                ('published_time', models.TimeField(db_index=True, null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438', blank=True)),
                ('subject_main', models.BooleanField(default=False, db_index=True, verbose_name='\u0433\u043b\u0430\u0432\u043d\u043e\u0435 \u0432 \u0441\u044e\u0436\u0435\u0442\u0435')),
                ('title', models.CharField(max_length=765, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('slug', models.SlugField(verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('author', models.TextField(verbose_name='\u0410\u0432\u0442\u043e\u0440', blank=True)),
                ('caption', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430', blank=True)),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435', blank=True)),
                ('is_hidden', models.BooleanField(default=True, db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0442\u0430\u044f')),
                ('is_advertising', models.BooleanField(default=False, db_index=True, verbose_name='\u0420\u0435\u043a\u043b\u0430\u043c\u043d\u0430\u044f')),
                ('is_important', models.BooleanField(default=False, help_text='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u0432 \u0431\u043b\u043e\u043a\u0435 \xab\u0413\u043b\u0430\u0432\u043d\u043e\u0435\xbb \u043d\u0430 \u0438\u043d\u0434\u0435\u043a\u0441\u0435 \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439', db_index=True, verbose_name='\u0413\u043b\u0430\u0432\u043d\u043e\u0435')),
                ('is_unkind', models.BooleanField(default=False, db_index=True, verbose_name='\u041d\u0435\u0434\u043e\u0431\u0440\u0430\u044f')),
                ('is_super', models.BooleanField(default=False, help_text='\u041c\u043e\u0436\u0435\u0442 \u0431\u044b\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0434\u0438\u043d \u0441\u0443\u043f\u0435\u0440-\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b.', db_index=True, verbose_name='\u0421\u0443\u043f\u0435\u0440-\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('comments_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432', editable=False)),
                ('home_position', models.BigIntegerField(default=irk.utils.helpers.big_int_from_time, verbose_name='\u0421\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0430 \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0435', editable=False, db_index=True)),
                ('stick_position', models.PositiveSmallIntegerField(db_index=True, null=True, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0437\u0430\u043a\u0440\u0435\u043f\u043b\u0435\u043d\u0438\u044f', blank=True)),
                ('stick_date', models.DateTimeField(db_index=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u0437\u0430\u043a\u0440\u0435\u043f\u043b\u0435\u043d\u0438\u044f', blank=True)),
                ('comment_disable_stamp', models.DateField(db_index=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u0442\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432', blank=True)),
                ('serialized_sites', models.CharField(max_length=255, verbose_name='\u0421\u0435\u0440\u0438\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u0441\u043f\u0438\u0441\u043e\u043a \u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440\u043e\u0432 \u0440\u0430\u0437\u0434\u0435\u043b\u043e\u0432', blank=True)),
                ('views_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u044b', editable=False, db_index=True)),
                ('popularity', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u043f\u0443\u043b\u044f\u0440\u043d\u043e\u0441\u0442\u044c', editable=False, db_index=True)),
                ('is_number_of_day', models.BooleanField(default=False, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u043a\u0430\u043a "\u0427\u0438\u0441\u043b\u043e \u0434\u043d\u044f"')),
                ('number_of_day_number', models.CharField(default=b'', max_length=250, verbose_name='\u0427\u0438\u0441\u043b\u043e', blank=True)),
                ('number_of_day_text', models.TextField(default=b'', verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('vk_share_cnt', models.PositiveIntegerField(default=0, verbose_name='\u0412\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0435')),
                ('tw_share_cnt', models.PositiveIntegerField(default=0, verbose_name='\u0422\u0432\u0438\u0442\u0442\u0435\u0440')),
                ('ok_share_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041e\u0434\u043d\u043e\u043a\u043b\u0430\u0441\u0441\u043d\u0438\u043a\u0438')),
                ('fb_share_cnt', models.PositiveIntegerField(default=0, verbose_name='Facebook')),
            ],
            options={
                'permissions': (('can_see_hidden', 'Can see hidden materials'),),
                'db_table': 'news_basematerial',
                'verbose_name': '\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b',
                'verbose_name_plural': '\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u044b',
            },
        ),
        migrations.CreateModel(
            name='BaseNewsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.PositiveSmallIntegerField(default=1, verbose_name='\u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435', choices=[(1, '\u043d\u043e\u0432\u0430\u044f'), (2, '\u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0430'), (3, '\u043d\u0435 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0430')])),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u0430')),
                ('sent', models.DateTimeField(null=True, verbose_name='\u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430')),
                ('sent_cnt', models.PositiveIntegerField(default=0, verbose_name='\u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a\u0438', editable=False)),
                ('views_cnt', models.PositiveIntegerField(default=0, verbose_name='\u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u044b', editable=False)),
            ],
            options={
                'verbose_name': '\u043d\u043e\u0432\u043e\u0441\u0442\u043d\u0430\u044f \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0430',
                'verbose_name_plural': '\u043d\u043e\u0432\u043e\u0441\u0442\u043d\u044b\u0435 \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('slug', models.CharField(max_length=50, verbose_name='\u0410\u043b\u0438\u0430\u0441', db_index=True)),
                ('position_count', models.PositiveSmallIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u0437\u0438\u0446\u0438\u0439')),
            ],
            options={
                'verbose_name': '\u0411\u043b\u043e\u043a \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u043e\u0432',
                'verbose_name_plural': '\u0411\u043b\u043e\u043a\u0438 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u043e\u0432',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_custom', models.BooleanField(default=False, verbose_name='\u0421\u043f\u0435\u0446\u0438\u0430\u043b\u044c\u043d\u0430\u044f \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f')),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('slug', models.SlugField(verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.news.models.category_image_upload_to, null=True, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
            ],
            options={
                'db_table': 'news_categories',
                'verbose_name': '\u0440\u0443\u0431\u0440\u0438\u043a\u0430',
                'verbose_name_plural': '\u0440\u0443\u0431\u0440\u0438\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='Flash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instance_id', models.CharField(max_length=20, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440', blank=True)),
                ('type', models.PositiveIntegerField(verbose_name='\u0422\u0438\u043f \u043d\u043e\u0432\u043e\u0441\u0442\u0438', choices=[(1, 'Twitter'), (2, 'SMS'), (3, '\u0421\u0430\u0439\u0442'), (4, '\u0412\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0435 \u0414\u0422\u041f')])),
                ('username', models.CharField(max_length=15, verbose_name='\u0410\u0432\u0442\u043e\u0440', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True)),
                ('content', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('visible', models.BooleanField(default=True, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c')),
                ('created', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('comments_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432', editable=False)),
                ('video_thumbnail', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/news/flash', null=True, verbose_name='\u041f\u0440\u0435\u0432\u044c\u044e \u0432\u0438\u0434\u0435\u043e', blank=True)),
            ],
            options={
                'db_table': 'news_flash',
                'verbose_name': '\u043d\u0430\u0440\u043e\u0434\u043d\u0430\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u044c',
                'verbose_name_plural': '\u043d\u0430\u0440\u043e\u0434\u043d\u044b\u0435 \u043d\u043e\u0432\u043e\u0441\u0442\u0438',
            },
        ),
        migrations.CreateModel(
            name='FlashBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pattern', models.CharField(max_length=50, verbose_name='\u0418\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f')),
            ],
            options={
                'db_table': 'news_flash_block',
                'verbose_name': '\u0431\u0430\u043d \u043f\u043e \u043d\u043e\u043c\u0435\u0440\u0443 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430 \u0438\u043b\u0438 twitter',
                'verbose_name_plural': '\u0431\u0430\u043d \u043f\u043e \u043d\u043e\u043c\u0435\u0440\u0443 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430 \u0438\u043b\u0438 twitter',
            },
        ),
        migrations.CreateModel(
            name='Live',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_finished', models.BooleanField(default=False, verbose_name='\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430')),
            ],
            options={
                'db_table': 'news_live',
                'verbose_name': '\u043e\u043d\u043b\u0430\u0439\u043d-\u0442\u0440\u0430\u043d\u0441\u043b\u044f\u0446\u0438\u044f',
                'verbose_name_plural': '\u043e\u043d\u043b\u0430\u0439\u043d-\u0442\u0440\u0430\u043d\u0441\u043b\u044f\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='LiveEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('is_important', models.BooleanField(default=False, verbose_name='\u0412\u0430\u0436\u043d\u043e\u0435')),
                ('created', models.TimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/news/live', null=True, verbose_name='\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430', blank=True)),
            ],
            options={
                'db_table': 'news_live_entries',
            },
        ),
        migrations.CreateModel(
            name='Mailer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mails', models.TextField(help_text='\u0421\u043f\u0438\u0441\u043e\u043a email \u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e', verbose_name='\u0421\u043f\u0438\u0441\u043e\u043a \u0430\u0434\u0440\u0435\u0441\u043e\u0432')),
                ('title', models.CharField(max_length=255, null=True, verbose_name='\u0422\u0435\u043c\u0430 \u043f\u0438\u0441\u044c\u043c\u0430', blank=True)),
                ('file', irk.utils.fields.file.FileRemovableField(upload_to=b'img/site/news/mailer_files', null=True, verbose_name='\u0424\u0430\u0439\u043b', blank=True)),
                ('text', models.TextField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('stamp', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438')),
            ],
            options={
                'verbose_name': '\u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0430 \u0434\u043b\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u043e\u043d\u043d\u044b\u0445 \u0430\u0433\u0435\u043d\u0441\u0442\u0432',
                'verbose_name_plural': '\u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u0434\u043b\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u043e\u043d\u043d\u044b\u0445 \u0430\u0433\u0435\u043d\u0441\u0442\u0432',
            },
        ),
        migrations.CreateModel(
            name='MaterialNewsletterRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.BigIntegerField(default=irk.utils.helpers.big_int_from_time, verbose_name='\u043f\u043e\u0437\u0438\u0446\u0438\u044f', editable=False, db_index=True)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': '\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438',
                'verbose_name_plural': '\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u044b \u0440\u0430\u0441\u0441\u044b\u043b\u043e\u043a',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0424\u0418\u041e')),
                ('caption', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430')),
                ('bio', models.TextField(verbose_name='\u0411\u0438\u043e\u0433\u0440\u0430\u0444\u0438\u044f')),
            ],
            options={
                'db_table': 'news_persons',
                'verbose_name': '\u043f\u0435\u0440\u0441\u043e\u043d\u0430',
                'verbose_name_plural': '\u043f\u0435\u0440\u0441\u043e\u043d\u044b',
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.PositiveSmallIntegerField(verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043f\u043e\u0437\u0438\u0446\u0438\u0438')),
                ('object_id', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['number'],
                'verbose_name': '\u041f\u043e\u0437\u0438\u0446\u0438\u044f',
                'verbose_name_plural': '\u041f\u043e\u0437\u0438\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='Press',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stamp', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438')),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('content', models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
                ('author', models.CharField(max_length=255, verbose_name='\u0410\u0432\u0442\u043e\u0440')),
            ],
            options={
                'db_table': 'news_presses',
                'verbose_name': '\u043f\u0440\u0435\u0441\u0441-\u0440\u0435\u043b\u0438\u0437',
                'verbose_name_plural': '\u043f\u0440\u0435\u0441\u0441-\u0440\u0435\u043b\u0438\u0437\u044b',
            },
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('is_hidden', models.BooleanField(default=False, verbose_name='\u0421\u043a\u0440\u044b\u0442\u0430\u044f')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': '\u0446\u0438\u0442\u0430\u0442\u0430',
                'verbose_name_plural': '\u0446\u0438\u0442\u0430\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='Special',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('url', models.URLField(verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
            ],
            options={
                'db_table': 'news_special_projects',
                'verbose_name': '\u0441\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442',
                'verbose_name_plural': '\u0441\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('social_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 940x445', upload_to=irk.news.models.social_card_upload_to, null=True, verbose_name='\u0424\u043e\u043d \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('social_text', models.CharField(help_text='100 \u0437\u043d\u0430\u043a\u043e\u0432', max_length=100, verbose_name='\u0422\u0435\u043a\u0441\u0442 \u043a\u0430\u0440\u0442\u043e\u0447\u043a\u0438', blank=True)),
                ('social_label', models.CharField(help_text='50 \u0437\u043d\u0430\u043a\u043e\u0432', max_length=50, verbose_name='\u041c\u0435\u0442\u043a\u0430', blank=True)),
                ('social_card', models.ImageField(upload_to=irk.news.models.social_card_upload_to, null=True, verbose_name='\u041a\u0430\u0440\u0442\u043e\u0447\u043a\u0430 \u0434\u043b\u044f \u0441\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0445 \u0441\u0435\u0442\u0435\u0439', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('caption_small', models.TextField(verbose_name='\u043a\u0440\u0430\u0442\u043a\u043e\u0435 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('caption', models.TextField(verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('slug', models.SlugField(verbose_name='\u0430\u043b\u0438\u0430\u0441')),
                ('background_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f: 1920x250', upload_to=b'img/site/news/subject', null=True, verbose_name='\u0444\u043e\u043d\u043e\u0432\u043e\u0435 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('show_on_home', models.BooleanField(default=False, help_text='\u0421\u044e\u0436\u0435\u0442 \u0434\u043e\u043b\u0436\u0435\u043d \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u0442\u044c \u043c\u0438\u043d\u0438\u043c\u0443\u043c 2 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430 \u0438 3 \u043d\u043e\u0432\u043e\u0441\u0442\u0438', db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')),
                ('home_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f: 1920x400', upload_to=b'img/site/news/subject', null=True, verbose_name='\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0434\u043b\u044f \u0433\u043b\u0430\u0432\u043d\u043e\u0439', blank=True)),
            ],
            options={
                'db_table': 'news_subjects',
                'verbose_name': '\u0441\u044e\u0436\u0435\u0442',
                'verbose_name_plural': '\u0441\u044e\u0436\u0435\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('email', models.EmailField(max_length=40, serialize=False, verbose_name='E-mail', primary_key=True)),
                ('hash', models.CharField(max_length=40, editable=False)),
                ('is_active', models.BooleanField(default=True, db_index=True, verbose_name='\u0410\u043a\u0442\u0438\u0432\u0438\u0440\u043e\u0432\u0430\u043d')),
                ('hash_stamp', models.DateTimeField(default=datetime.datetime.now, null=True, editable=False, blank=True)),
            ],
            options={
                'db_table': 'news_distribution_subscribers',
                'verbose_name': '\u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a',
                'verbose_name_plural': '\u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='TextBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('content', models.CharField(max_length=255, verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435')),
                ('slug', models.CharField(max_length=50, verbose_name='\u0410\u043b\u0438\u0430\u0441', db_index=True)),
            ],
            options={
                'verbose_name': '\u0422\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0439 \u0431\u043b\u043e\u043a',
                'verbose_name_plural': '\u0422\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0435 \u0431\u043b\u043e\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='UrgentNews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('is_visible', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c')),
                ('created', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
            ],
            options={
                'db_table': 'news_urgent',
                'verbose_name': '\u0441\u0440\u043e\u0447\u043d\u0430\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u044c',
                'verbose_name_plural': '\u0441\u0440\u043e\u0447\u043d\u044b\u0435 \u043d\u043e\u0432\u043e\u0441\u0442\u0438',
            },
        ),
        migrations.CreateModel(
            name='Words',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(help_text='\u0427\u0435\u0440\u0435\u0437 \u043f\u0440\u043e\u0431\u0435\u043b', verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430 \u043a\u043b\u044e\u0447\u0435\u0432\u044b\u0445 \u0441\u043b\u043e\u0432')),
            ],
            options={
                'verbose_name': '\u0433\u0440\u0443\u043f\u043f\u0430 \u043a\u043b\u044e\u0447\u0435\u0432\u044b\u0445 \u0441\u043b\u043e\u0432',
                'verbose_name_plural': '\u0433\u0440\u0443\u043f\u043f\u044b \u043a\u043b\u044e\u0447\u0435\u0432\u044b\u0445 \u0441\u043b\u043e\u0432',
            },
        ),
    ]
