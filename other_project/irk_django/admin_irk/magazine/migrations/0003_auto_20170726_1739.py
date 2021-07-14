# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0002_auto_20170418_1503'),
        ('magazine', '0002_auto_20170704_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='magazine',
            name='banner_comment',
            field=models.ForeignKey(related_name='magazinet_banner_comment', verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0442\u0435\u043a\u0441\u0442\u043e\u043c \u0438 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u043c\u0438', blank=True, to='adv.Place', null=True),
        ),
        migrations.AddField(
            model_name='magazine',
            name='banner_right',
            field=models.ForeignKey(related_name='magazine_banner_right', verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0431\u0430\u043d\u043d\u0435\u0440\u0430 \u0432 \u043f\u0440\u0430\u0432\u043e\u0439 \u043a\u043e\u043b\u043e\u043d\u043a\u0435', blank=True, to='adv.Place', null=True),
        ),
        migrations.AddField(
            model_name='magazine',
            name='branding_bottom',
            field=models.ForeignKey(related_name='magazine_branding_bottom', verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0431\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u0432\u043d\u0438\u0437\u0443 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b', blank=True, to='adv.Place', null=True),
        ),
    ]
