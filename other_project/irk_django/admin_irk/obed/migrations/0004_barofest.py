# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0003_auto_20170324_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='BarofestParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('establishment', models.OneToOneField(related_name='establishment_barofest', verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='obed.Establishment')),
            ],
            options={
                'verbose_name': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a \u0411\u0413\u0424 2018',
                'verbose_name_plural': '\u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u0438 \u0431\u0430\u0440\u043e\u0444\u0435\u0441\u0442\u0430 2018',
            },
        ),
        migrations.AlterField(
            model_name='review',
            name='columnist',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='\u0420\u0435\u0446\u0435\u043d\u0437\u0435\u043d\u0442', choices=[(b'siropova', '\u041b\u0438\u0437\u0430 \u0421\u0438\u0440\u043e\u043f\u043e\u0432\u0430'), (b'abram', '\u0410\u0431\u0440\u0430\u043c \u0414\u044e\u0440\u0441\u043e'), (b'buuzin', '\u041c\u0438\u0445\u0430\u0438\u043b \u0411\u0443\u0443\u0437\u0438\u043d'), (b'chesnok', '\u0410\u043d\u0430\u0442\u043e\u043b\u0438\u0439 \u0427\u0435\u0441\u043d\u043e\u043a\u043e\u0432'), (b'olivie', '\u041a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u0438\u043d \u041e\u043b\u0438\u0432\u044c\u0435'), (b'anteater', '\u0410\u0440\u043a\u0430\u0434\u0438\u0439 \u041c\u0443\u0440\u0430\u0432\u044c\u0435\u0434'), (b'grill', '\u0415\u0432\u0430 \u0413\u0440\u0438\u043b\u044c'), (b'terkin', '\u041f\u0451\u0442\u0440 \u0422\u0451\u0440\u043a\u0438\u043d')]),
        ),
    ]
