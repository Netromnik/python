# Generated by Django 3.1.2 on 2020-11-14 14:45

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import base.managers.group
import base.models_i.file
import base.models_i.tasks


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('base', '0003_task_date_due'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mesenge', models.TextField(verbose_name='messenge')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            managers=[
                ('obj', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='CollectMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'Коллекция файлов',
                'verbose_name_plural': 'Коллекции файлов',
            },
            managers=[
                ('obj', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='documents/%Y/%m/%d/', validators=[base.models_i.file.validate_file])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('collect', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='colectFile', to='base.collectmedia')),
            ],
            options={
                'verbose_name': 'Файл',
                'verbose_name_plural': 'Файлы',
            },
            managers=[
                ('obj', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='LogHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='action time')),
                ('object_id', models.TextField(blank=True, null=True, verbose_name='object id')),
                ('action_flag', models.PositiveSmallIntegerField(choices=[(1, 'Addition'), (2, 'Change'), (3, 'Deletion')], verbose_name='action flag')),
                ('change_message', models.TextField(blank=True, verbose_name='change message')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype', verbose_name='content type')),
            ],
            options={
                'verbose_name': 'История',
                'verbose_name_plural': 'История',
                'db_table': 'log_history',
                'ordering': ['-action_time'],
            },
            managers=[
                ('alert_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelOptions(
            name='customgroup',
            options={'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='queue',
            options={'verbose_name': 'Очередь', 'verbose_name_plural': 'Очереди'},
        ),
        migrations.AlterModelOptions(
            name='stream',
            options={'verbose_name': 'Поток', 'verbose_name_plural': 'Потоки'},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'verbose_name': 'Задача', 'verbose_name_plural': 'Задачи'},
        ),
        migrations.AlterModelManagers(
            name='customgroup',
            managers=[
                ('obj', base.managers.group.GroupManager()),
            ],
        ),
        migrations.AddField(
            model_name='stream',
            name='in_public',
            field=models.BooleanField(default=True, help_text='Будет использованно для отображения в форму', verbose_name='Отображения'),
        ),
        migrations.AddField(
            model_name='task',
            name='chenge_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='chenge_user', to=settings.AUTH_USER_MODEL, verbose_name='Последний изменивший'),
        ),
        migrations.AlterField(
            model_name='customgroup',
            name='name',
            field=models.CharField(max_length=128, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='task',
            name='asignet_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='asing_to', to=settings.AUTH_USER_MODEL, verbose_name='Ответственный'),
        ),
        migrations.AlterField(
            model_name='task',
            name='autors',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='autorTask', to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AlterField(
            model_name='task',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='task',
            name='date_due',
            field=models.DateField(default=base.models_i.tasks.set_time_default, verbose_name='Дата оканчания'),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('W', 'Ожидает'), ('O', 'Открыта'), ('S', 'Решено'), ('C', 'Закрыто')], max_length=1, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='task',
            name='stream',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='base.stream', verbose_name='Поток'),
        ),
        migrations.AlterField(
            model_name='task',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.DeleteModel(
            name='History',
        ),
        migrations.AddField(
            model_name='loghistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='chatmodel',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='base.task', verbose_name='task'),
        ),
        migrations.AddField(
            model_name='chatmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='task',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='file_re', to='base.file', verbose_name='Файл'),
        ),
        migrations.AlterField(
            model_name='task',
            name='stream',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='base.stream',
                                    verbose_name='Категория'),
        ),
        migrations.AlterModelOptions(
            name='stream',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),

    ]
