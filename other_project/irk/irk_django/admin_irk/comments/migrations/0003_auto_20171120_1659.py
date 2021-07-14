# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0002_auto_20170529_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('action', models.SmallIntegerField(verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435', choices=[(1, '\u0423\u0434\u0430\u043b\u0435\u043d\u0438\u0435'), (2, '\u0412\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435')])),
                ('comment', models.ForeignKey(verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', to='comments.Comment')),
                ('user', models.ForeignKey(verbose_name='\u0418\u0437\u043c\u0435\u043d\u0438\u043b', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435',
                'verbose_name_plural': '\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f',
            },
        ),
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True,
                                       verbose_name='\u0434\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f',
                                       db_index=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='modified',
            field=models.DateTimeField(auto_now=True,
                                       verbose_name='\u0434\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f',
                                       db_index=True),
        ),
    ]
