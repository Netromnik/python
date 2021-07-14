# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file
from django.conf import settings
import irk.experts.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expert',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('specialist', models.TextField(verbose_name='\u042d\u043a\u0441\u043f\u0435\u0440\u0442')),
                ('avatar', irk.utils.fields.file.ImageRemovableField(help_text='\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0432 \u043e\u0442\u0432\u0435\u0442\u0430\u0445 \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u0430.<br />\u0424\u043e\u0442\u043e \u0434\u043e\u043b\u0436\u043d\u043e \u0431\u044b\u0442\u044c \u043a\u0432\u0430\u0434\u0440\u0430\u0442\u043d\u044b\u043c! \u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u043c\u0435\u0440 200x200.', upload_to=b'img/site/experts/avatars/', null=True, verbose_name='\u0410\u0432\u0430\u0442\u0430\u0440\u043a\u0430', blank=True)),
                ('signature', models.CharField(help_text='\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0432 \u043e\u0442\u0432\u0435\u0442\u0430\u0445 \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u0430.', max_length=100, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u044c \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u0430', blank=True)),
                ('contacts', models.TextField(verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435', blank=True)),
                ('stamp_end', models.DateField(verbose_name='\u041a\u043e\u043d\u0435\u0446')),
                ('stamp_publ', models.DateField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438 \u043e\u0442\u0432\u0435\u0442\u043e\u0432', blank=True)),
                ('questions_count', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0432\u043e\u043f\u0440\u043e\u0441\u043e\u0432', editable=False)),
                ('is_answered', models.BooleanField(default=False, verbose_name='\u041e\u0442\u0432\u0435\u0442\u044b \u0434\u0430\u043d\u044b')),
                ('is_consultation', models.BooleanField(default=False, verbose_name='\u041a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u0446\u0438\u044f')),
                ('is_main', models.BooleanField(default=False, verbose_name='\u0413\u043b\u0430\u0432\u043d\u0430\u044f \u043a\u043e\u043d\u0444\u0435\u0440\u0435\u043d\u0446\u0438\u044f')),
                ('is_announce', models.BooleanField(default=False, verbose_name='\u0410\u043d\u043e\u043d\u0441\u0438\u0440\u043e\u0432\u0430\u0442\u044c')),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u041e\u043f\u0442\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u043c\u0435\u0440 \u0444\u043e\u0442\u043e 705\u0445470, \u043c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439 460\u0445307. \u041f\u0440\u043e\u043f\u043e\u0440\u0446\u0438\u044f 3:2.', upload_to=b'img/site/experts/', null=True, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', blank=True)),
                ('wide_image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.experts.models.expert_image_upload_to, null=True, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('picture', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/experts/', null=True, verbose_name='\u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430', blank=True)),
                ('image_title', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u044c \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f', blank=True)),
            ],
            options={
                'db_table': 'experts',
                'verbose_name': '\u043a\u043e\u043d\u0444\u0435\u0440\u0435\u043d\u0446\u0438\u044f',
                'verbose_name_plural': '\u043a\u043e\u043d\u0444\u0435\u0440\u0435\u043d\u0446\u0438\u0438',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.TextField(verbose_name='\u0412\u043e\u043f\u0440\u043e\u0441')),
                ('answer', models.TextField(verbose_name='\u041e\u0442\u0432\u0435\u0442')),
                ('created', models.DateTimeField()),
                ('expert', models.ForeignKey(to='experts.Expert')),
                ('same_as', models.ForeignKey(related_name='identical', verbose_name='\u041e\u0434\u0438\u043d\u0430\u043a\u043e\u0432 \u0441', blank=True, to='experts.Question', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'expert_questions',
            },
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('expert', models.ForeignKey(verbose_name='\u042d\u043a\u0441\u043f\u0435\u0440\u0442', to='experts.Expert')),
                ('user', models.ForeignKey(related_name='expert_subscriber', verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u0430',
                'verbose_name_plural': '\u043f\u043e\u0434\u043f\u0438\u0441\u0447\u0438\u043a\u0438 \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u0430',
            },
        ),
    ]
