# Generated by Django 3.2 on 2021-04-27 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_workselect'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='work',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.workselect'),
        ),
    ]