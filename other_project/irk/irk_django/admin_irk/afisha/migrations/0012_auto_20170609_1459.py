# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

sql_forwards = '''
UPDATE afisha_ramblersession s
SET s.show_datetime = CASE
    WHEN TIME(s.datetime) <= TIME('06:00') THEN DATE_SUB(s.datetime, INTERVAL 1 DAY)
    ELSE s.datetime
    END;

UPDATE afisha_kinomaxsession s
SET s.show_datetime = CASE
    WHEN TIME(s.datetime) <= TIME('06:00') THEN DATE_SUB(s.datetime, INTERVAL 1 DAY)
    ELSE s.datetime
    END;
'''

sql_backwards = '''
UPDATE afisha_ramblersession s
SET s.show_datetime = NULL;

UPDATE afisha_kinomaxsession s
SET s.show_datetime = NULL;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0011_auto_20170609_1138'),
    ]

    operations = [
        migrations.RunSQL(sql_forwards, sql_backwards),
    ]
