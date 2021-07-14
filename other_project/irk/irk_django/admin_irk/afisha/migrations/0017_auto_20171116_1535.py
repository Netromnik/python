# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_block(apps, schema_editor):
    Block = apps.get_model('news', 'Block')

    block = Block()
    block.name = ''
    block.slug = 'afisha_read_sidebar'
    block.position_count = 3
    block.save()

    Block.objects.filter(slug='afisha_index_sidebar').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0016_auto_20171019_1551'),
    ]

    operations = [
        migrations.RunPython(create_block),
    ]
