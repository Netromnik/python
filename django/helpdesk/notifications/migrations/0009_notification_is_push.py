# Generated by Django 2.2.19 on 2021-02-25 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0008_index_together_recipient_unread'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_push',
            field=models.BooleanField(default=True),
        ),
    ]
