# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    def fix_disable_comments(apps, schema_editor):
        BaseMaterial = apps.get_model("news", "BaseMaterial")

        from django.db import connection
        cursor = connection.cursor()

        sql = "UPDATE {0} SET disable_comments=hide_comments".format(BaseMaterial._meta.db_table)
        cursor.execute(sql)
        sql = "UPDATE {0} SET hide_comments=0".format(BaseMaterial._meta.db_table)
        cursor.execute(sql)

    dependencies = [
        ('news', '0005_auto_20170220_1505'),
    ]

    operations = [
        migrations.RunPython(fix_disable_comments, atomic=False),
    ]
