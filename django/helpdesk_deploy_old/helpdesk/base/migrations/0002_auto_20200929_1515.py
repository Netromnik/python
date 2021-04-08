# Generated by Django 2.2.16 on 2020-09-29 15:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='task',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='taskH', to='base.Task'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='queue',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='queue_set', related_query_name='queue', to='base.CustomGroup', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='stream',
            name='queue',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='base.Queue'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='asignet_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='asing_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='task',
            name='autors',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='autorTask', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='stream',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='base.Stream'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='base.CustomGroup', verbose_name='groups'),
        ),
    ]