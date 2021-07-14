# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0012_delete_text_block'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0443\u0441\u043a\u0430 \u0437\u0430\u0434\u0430\u0447\u0438')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0435 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u0435')),
                ('task', models.CharField(default=b'publish', max_length=250, verbose_name='\u0417\u0430\u0434\u0430\u0447\u0430')),
                ('state', models.CharField(default=b'scheduled', max_length=50, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[(b'scheduled', '\u0417\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0430'), (b'done', '\u0423\u0441\u043f\u0435\u0448\u043d\u043e \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430'), (b'canceled', '\u0411\u044b\u043b\u0430 \u0437\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0430, \u043d\u043e \u043e\u0442\u043c\u0435\u043d\u0438\u043b\u0430\u0441\u044c')])),
                ('log', models.CharField(default=b'', max_length=1000, verbose_name='\u041b\u043e\u0433 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f', blank=True)),
            ],
            options={
                'verbose_name': '\u0417\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u0430\u044f \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u044f',
                'verbose_name_plural': '\u0417\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u043f\u0443\u0431\u043b\u0438\u043a\u0430\u0446\u0438\u0438',
            },
        ),
        migrations.AlterField(
            model_name='basematerial',
            name='disable_comments',
            field=models.BooleanField(default=False, help_text='\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u0432\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f', db_index=True, verbose_name='\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='basematerial',
            name='hide_comments',
            field=models.BooleanField(default=False, help_text='\u043e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u044b \u0431\u0435\u0437 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043f\u0440\u043e 24 \u0447\u0430\u0441\u0430', db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438'),
        ),
        migrations.AlterField(
            model_name='flash',
            name='disable_comments',
            field=models.BooleanField(default=False, help_text='\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u0432\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f', db_index=True, verbose_name='\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='flash',
            name='hide_comments',
            field=models.BooleanField(default=False, help_text='\u043e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u044b \u0431\u0435\u0437 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043f\u0440\u043e 24 \u0447\u0430\u0441\u0430', db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438'),
        ),
        migrations.AddField(
            model_name='scheduledtask',
            name='material',
            field=models.OneToOneField(related_name='scheduled_task', to='news.BaseMaterial'),
        ),
    ]
