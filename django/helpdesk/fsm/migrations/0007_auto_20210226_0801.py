# Generated by Django 2.2.19 on 2021-02-26 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0006_auto_20210225_0750'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='raiting',
            field=models.IntegerField(default=-1, verbose_name='Рейтинг'),
        ),
        migrations.AddField(
            model_name='task',
            name='the_importance',
            field=models.CharField(choices=[('Открыта', 'Открыта'), ('Ваполняется', 'Ваполняется'), ('Решена', 'Решена'), ('Переоткрыта', 'Переоткрыта'), ('Ошибка', 'Ошибка'), ('Закрыта', 'Закрыта')], default='Ваполняется', max_length=26, verbose_name='Уровень важности'),
        ),
    ]
