# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='image',
            field=irk.utils.fields.file.ImageRemovableField(help_text='\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c\u044b\u0435 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 \u0434\u043e\u043b\u0436\u043d\u044b \u0431\u044b\u0442\u044c \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 jpeg, gif, png. \u0420\u0430\u0437\u043c\u0435\u0440 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438 \u043f\u043e \u0448\u0438\u0440\u0438\u043d\u0435 - 580x, \u043f\u043e \u0432\u044b\u0441\u043e\u0442\u0435 - 250px.', upload_to=b'img/site/tourism/tour/', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True),
        ),
    ]
