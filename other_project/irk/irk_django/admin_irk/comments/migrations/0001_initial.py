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
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442', blank=True)),
                ('ip', models.BigIntegerField(verbose_name='IP', null=True, editable=False, blank=True)),
                ('status', models.PositiveSmallIntegerField(default=1, db_index=True, verbose_name='\u0441\u0442\u0430\u0442\u0443\u0441', choices=[(1, '\u0432\u0438\u0434\u0435\u043d'), (2, '\u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0435 \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u0435'), (3, '\u043f\u0440\u044f\u043c\u043e\u0435 \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u0435'), (4, '\u0441\u043f\u0430\u043c')])),
                ('is_first', models.BooleanField(default=False, db_index=True, verbose_name='\u043f\u0435\u0440\u0432\u044b\u0439 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f')),
                ('created', models.DateTimeField(db_index=True, verbose_name='\u0434\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('modified', models.DateTimeField(db_index=True, verbose_name='\u0434\u0430\u0442\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f')),
                ('target_id', models.PositiveIntegerField(db_index=True)),
                ('message_id', models.IntegerField(null=True, db_index=True)),
                ('message_parent_id', models.IntegerField(null=True, db_index=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('parent', models.ForeignKey(related_name='answers', to='comments.Comment', null=True)),
                ('user', models.ForeignKey(related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439',
                'verbose_name_plural': '\u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='CommentClosure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('depth', models.IntegerField(db_index=True)),
                ('child', models.ForeignKey(related_name='commentclosure_parents', to='comments.Comment')),
                ('parent', models.ForeignKey(related_name='commentclosure_children', to='comments.Comment')),
            ],
            options={
                'db_table': 'comments_commentclosure',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentclosure',
            unique_together=set([('parent', 'child')]),
        ),
    ]
