# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('user_agent', models.CharField(default=b'', max_length=255, db_index=True, blank=True)),
                ('value', models.IntegerField()),
            ],
            options={
                'db_table': 'rating_values',
                'verbose_name': '\u0433\u043e\u043b\u043e\u0441',
                'verbose_name_plural': '\u0433\u043e\u043b\u043e\u0441\u0430',
            },
        ),
        migrations.CreateModel(
            name='RatingObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_pk', models.PositiveIntegerField()),
                ('total_cnt', models.PositiveIntegerField(default=0, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0433\u043e\u043b\u043e\u0441\u043e\u0432')),
                ('total_sum', models.IntegerField(default=0, verbose_name='\u0421\u0443\u043c\u043c\u0430 \u0433\u043e\u043b\u043e\u0441\u043e\u0432', db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'db_table': 'rating_objects',
                'verbose_name': '\u043e\u0431\u044a\u0435\u043a\u0442 \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u044f',
                'verbose_name_plural': '\u043e\u0431\u044a\u0435\u043a\u0442\u044b \u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u044f',
            },
        ),
        migrations.AddField(
            model_name='rate',
            name='obj',
            field=models.ForeignKey(related_name='rates', to='ratings.RatingObject'),
        ),
        migrations.AddField(
            model_name='rate',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='ratingobject',
            unique_together=set([('content_type', 'object_pk')]),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('obj', 'user')]),
        ),
    ]
