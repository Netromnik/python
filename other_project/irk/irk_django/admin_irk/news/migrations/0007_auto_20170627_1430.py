# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('magazine', '0001_initial'),
        ('news', '0006_auto_20170220_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='basematerial',
            name='magazine',
            field=models.ForeignKey(related_name='news_magazine_materials', verbose_name='\u0416\u0443\u0440\u043d\u0430\u043b', to='magazine.Magazine', null=True),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='magazine_author',
            field=models.ForeignKey(verbose_name='\u0410\u0432\u0442\u043e\u0440 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430 \u0432 \u0436\u0443\u0440\u043d\u0430\u043b\u0435', to='magazine.MagazineAuthor', null=True),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='magazine_image',
            field=irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/news/magazine', null=True, verbose_name='\u0424\u043e\u0442\u043e \u0434\u043b\u044f \u0436\u0443\u0440\u043d\u0430\u043b\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='magazine_position',
            field=models.IntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0432 \u0436\u0443\u0440\u043d\u0430\u043b\u0435', db_index=True),
        ),
    ]
