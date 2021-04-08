# Generated by Django 3.1.2 on 2020-12-10 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20201114_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectmedia',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='_collectmedia_groups_+', to='base.CustomGroup', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='collectmedia',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]