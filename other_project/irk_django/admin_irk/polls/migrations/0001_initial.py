# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.news.models
from django.conf import settings
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('start', models.DateField(db_index=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', blank=True)),
                ('end', models.DateField(db_index=True, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043a\u043e\u043d\u0446\u0430', blank=True)),
                ('votes_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0433\u043e\u043b\u043e\u0441\u043e\u0432', editable=False)),
                ('multiple', models.BooleanField(default=False, verbose_name='\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043e\u0442\u0432\u0435\u0442\u043e\u0432')),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u041e\u043f\u0442\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u043c\u0435\u0440 \u0444\u043e\u0442\u043e 620\u0445413. \u041f\u0440\u043e\u043f\u043e\u0440\u0446\u0438\u044f 3:2.', upload_to=irk.news.models.wide_image_upload_to, null=True, verbose_name='\u0421\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043d\u043e\u0435 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('show_image_on_read', models.BooleanField(default=False, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u0444\u043e\u0442\u043e \u043d\u0430 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0435 \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u044f')),
                ('image_label', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u044c \u0441\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043d\u043e\u0433\u043e \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f', blank=True)),
                ('w_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439.', upload_to=irk.news.models.wide_image_upload_to, null=True, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u043e\u0435 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('target_id', models.PositiveIntegerField(default=0)),
                ('target_ct', models.ForeignKey(blank=True, to='contenttypes.ContentType', help_text='\u041a \u0447\u0435\u043c\u0443 \u043f\u0440\u0438\u0432\u044f\u0437\u044b\u0432\u0430\u0442\u044c \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435', null=True, verbose_name='\u0422\u0438\u043f \u043e\u0431\u044a\u0435\u043a\u0442\u0430')),
            ],
            options={
                'db_table': 'polls_main',
                'verbose_name': '\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435',
                'verbose_name_plural': '\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u044f',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='PollChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255, verbose_name='\u0412\u0430\u0440\u0438\u0430\u043d\u0442 \u043e\u0442\u0432\u0435\u0442\u0430')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('votes_cnt', models.PositiveIntegerField(default=0)),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 60x60 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/polls/choice/', null=True, verbose_name='\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('poll', models.ForeignKey(to='polls.Poll')),
            ],
            options={
                'db_table': 'polls_choices',
                'verbose_name': '\u043e\u0442\u0432\u0435\u0442',
                'verbose_name_plural': '\u043e\u0442\u0432\u0435\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='PollVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.PositiveIntegerField(default=0, db_index=True)),
                ('choice', models.ForeignKey(to='polls.PollChoice')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'polls_votes',
                'verbose_name': '\u0433\u043e\u043b\u043e\u0441',
                'verbose_name_plural': '\u0433\u043e\u043b\u043e\u0441\u0430',
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('slug', models.SlugField(verbose_name='\u0410\u043b\u0438\u0430\u0441')),
                ('comments_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432', editable=False)),
            ],
            options={
                'verbose_name': '\u043e\u043f\u0440\u043e\u0441',
                'verbose_name_plural': '\u043e\u043f\u0440\u043e\u0441\u044b',
            },
        ),
    ]
