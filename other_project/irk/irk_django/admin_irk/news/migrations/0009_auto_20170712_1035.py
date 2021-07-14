# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_auto_20170707_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basematerial',
            name='magazine',
            field=models.ForeignKey(related_name='news_magazine_materials', verbose_name='\u0416\u0443\u0440\u043d\u0430\u043b', blank=True, to='magazine.Magazine', null=True),
        ),
        migrations.AlterField(
            model_name='basematerial',
            name='magazine_author',
            field=models.ForeignKey(verbose_name='\u0410\u0432\u0442\u043e\u0440 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430 \u0432 \u0436\u0443\u0440\u043d\u0430\u043b\u0435', blank=True, to='magazine.MagazineAuthor', null=True),
        ),
        migrations.AlterField(
            model_name='basematerial',
            name='magazine_position',
            field=models.IntegerField(default=0, db_index=True, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0432 \u0436\u0443\u0440\u043d\u0430\u043b\u0435', blank=True),
        ),
    ]
