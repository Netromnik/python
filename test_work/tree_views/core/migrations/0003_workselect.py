# Generated by Django 3.2 on 2021-04-27 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_customuser_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkSelect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=12)),
            ],
        ),
    ]
