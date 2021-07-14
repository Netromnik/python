# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import irk.utils.fields.onetoone
import irk.utils.db.models.fields.color
import irk.utils.fields.file
import irk.adv.models
from django.conf import settings
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('about', '0001_initial'),
        ('options', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=50, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435',
                'verbose_name_plural': '\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('url', models.CharField(max_length=200, null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True)),
                ('alt', models.CharField(max_length=255, null=True, verbose_name='Alt', blank=True)),
                ('bgcolor', irk.utils.db.models.fields.color.ColorField(help_text='\u0412 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 #13bf99', max_length=6, null=True, verbose_name='\u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430', blank=True)),
                ('all_sites', models.BooleanField(default=False, verbose_name='\u0412\u0441\u0435', editable=False)),
                ('pixel_audit', models.CharField(max_length=255, verbose_name='\u041a\u043e\u0434 \u0434\u043b\u044f \u043f\u0438\u043a\u0441\u0435\u043b\u044c-\u0430\u0443\u0434\u0438\u0442\u0430', blank=True)),
                ('show_time_start', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u043a\u0430\u0437\u0430 \u0441', blank=True)),
                ('show_time_end', models.TimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u043a\u0430\u0437\u0430 \u043f\u043e', blank=True)),
                ('width', models.PositiveSmallIntegerField(null=True, verbose_name='\u0448\u0438\u0440\u0438\u043d\u0430', blank=True)),
                ('height', models.PositiveSmallIntegerField(null=True, verbose_name='\u0432\u044b\u0441\u043e\u0442\u0430', blank=True)),
                ('roll_direction', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0440\u0430\u0437\u0432\u043e\u0440\u043e\u0442\u0430', choices=[(4, '\u041d\u0430\u043b\u0435\u0432\u043e'), (2, '\u041d\u0430\u043f\u0440\u0430\u0432\u043e')])),
                ('roll_width', models.PositiveSmallIntegerField(help_text='\u0423\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0432 \u043f\u0438\u043a\u0441\u0435\u043b\u044f\u0445', null=True, verbose_name='\u0428\u0438\u0440\u0438\u043d\u0430 \u0431\u0430\u043d\u043d\u0435\u0440\u0430 \u0432 \u0441\u0432\u0435\u0440\u043d\u0443\u0442\u043e\u043c \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0438', blank=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('iframe', models.TextField(help_text='\u041a\u043e\u0434 \u0432\u0438\u0434\u0430: &lt;iframe src=&quot;\u0410\u0414\u0420\u0415\u0421&quot; width=&quot;200&quot; height=&quot;300&quot; border=&quot;0&quot; frameborder=&quot;0&quot; scrolling=&quot;0&quot;&gt;&lt;/iframe&gt;', verbose_name='\u041a\u043e\u0434 iframe', blank=True)),
                ('is_client_rotate', models.BooleanField(default=False, verbose_name='\u0420\u043e\u0442\u0430\u0446\u0438\u044f \u043d\u0430 \u043a\u043b\u0438\u0435\u043d\u0442\u0435')),
            ],
            options={
                'verbose_name': '\u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0420\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u0435',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430')),
                ('to_date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f')),
                ('finalPrice', models.FloatField(default=0, null=True, verbose_name='\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0441\u043e \u0441\u043a\u0438\u0434\u043a\u043e\u0439', blank=True)),
                ('comment', models.TextField(verbose_name='\u041f\u0440\u0438\u043c\u0435\u0447\u0430\u043d\u0438\u0435', blank=True)),
                ('payed', models.BooleanField(default=False, verbose_name='\u041e\u043f\u043b\u0430\u0447\u0435\u043d\u043e')),
                ('cash', models.BooleanField(default=False, verbose_name='\u041d\u0430\u043b\u0438\u0447\u043d\u044b\u043c\u0438')),
                ('deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d\u043e')),
                ('sale', models.FloatField(default=0, null=True, verbose_name='\u0421\u043a\u0438\u0434\u043a\u0430 \u0432 \u043f\u0440\u043e\u0446\u0435\u043d\u0442\u0430\u0445', blank=True)),
                ('price', models.FloatField(default=0, null=True, verbose_name='\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c', blank=True)),
            ],
            options={
                'verbose_name': '\u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435',
                'verbose_name_plural': '\u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f',
                'permissions': (('can_generate_reports', 'Can generate reports'), ('can_edit_old_bookings', 'Can edit old bookings'), ('can_edit_not_own_bookings', 'Can edit not own bookings'), ('can_use_bookings_system', 'Can use booking system')),
            },
        ),
        migrations.CreateModel(
            name='BookingHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_action', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f')),
                ('action', models.ForeignKey(verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043d\u0430\u0434 \u0431\u0440\u043e\u043d\u044c\u044e', to='adv.Action')),
                ('booking', models.ForeignKey(verbose_name='\u0411\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435', to='adv.Booking')),
            ],
            options={
                'verbose_name': '\u043b\u043e\u0433 \u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f',
                'verbose_name_plural': '\u043b\u043e\u0433 \u0431\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f')),
                ('juridical_name', models.CharField(max_length=255, null=True, verbose_name='\u042e\u0440\u0438\u0434\u0438\u0447\u0435\u0441\u043a\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('address', models.TextField(null=True, verbose_name='\u0410\u0434\u0440\u0435\u0441 \u0434\u043e\u0441\u0442\u0430\u0432\u043a\u0438', blank=True)),
                ('ownership', models.CharField(default='\u041e\u041e\u041e', max_length=7, verbose_name='\u0424\u043e\u0440\u043c\u0430 \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u043e\u0441\u0442\u0438', choices=[('\u041e\u041e\u041e', '\u041e\u041e\u041e'), ('\u0417\u0410\u041e', '\u0417\u0410\u041e'), ('\u041e\u0410\u041e', '\u041e\u0410\u041e'), ('\u041d\u041e\u0423\u0414\u041e', '\u041d\u041e\u0423\u0414\u041e'), ('\u0418\u041f', '\u0418\u041f'), ('\u0427\u041f', '\u0427\u041f')])),
                ('info', models.TextField(default=b'', verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f', blank=True)),
                ('is_deleted', models.BooleanField(default=False, db_index=True, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d')),
                ('is_active', models.BooleanField(default=True, db_index=True, verbose_name='\u041d\u0435 \u0432 \u0447\u0435\u0440\u043d\u043e\u043c \u0441\u043f\u0438\u0441\u043a\u0435')),
                ('cause', models.TextField(default=b'', verbose_name='\u041f\u0440\u0438\u0447\u0438\u043d\u0430 \u0437\u0430\u043d\u0435\u0441\u0435\u043d\u0438\u044f \u0432 \u0447\u0435\u0440\u043d\u044b\u0439 \u0441\u043f\u0438\u0441\u043e\u043a', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': '\u043a\u043b\u0438\u0435\u043d\u0442\u0430',
                'verbose_name_plural': '\u043a\u043b\u0438\u0435\u043d\u0442\u044b',
                'permissions': (('can_reassign_manager', 'Can reassign manager'),),
            },
        ),
        migrations.CreateModel(
            name='ClientType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255, verbose_name='\u0422\u0438\u043f')),
            ],
            options={
                'verbose_name': '\u0442\u0438\u043f \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0438',
                'verbose_name_plural': '\u0442\u0438\u043f\u044b \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0446\u0438\u0439',
            },
        ),
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.datetime.now, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438', blank=True)),
                ('time', models.TimeField(default=None, null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438', blank=True)),
                ('result', models.TextField(default=b'', null=True, verbose_name='\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442', blank=True)),
                ('target', models.TextField(default=b'', max_length=100, null=True, verbose_name='\u041f\u0440\u0438\u043c\u0435\u0447\u0430\u043d\u0438\u0435', blank=True)),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0435\u043d\u0430')),
                ('is_done', models.BooleanField(default=False, verbose_name='\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430')),
                ('notify_time', models.TimeField(default=None, null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u044f \u0434\u043e \u0441\u043e\u0431\u044b\u0442\u0438\u044f', blank=True)),
                ('next_communication', models.DateField(default=None, null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u0439 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438', blank=True)),
                ('booking', models.ForeignKey(default=None, blank=True, to='adv.Booking', null=True, verbose_name='\u0411\u0440\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('client', models.ForeignKey(verbose_name='\u041a\u043b\u0438\u0435\u043d\u0442', to='adv.Client')),
            ],
            options={
                'verbose_name': '\u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u044f',
                'verbose_name_plural': '\u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='CommunicationHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_action', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f')),
                ('action', models.ForeignKey(verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043d\u0430\u0434 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0435\u0439', to='adv.Action')),
                ('communication', models.ForeignKey(verbose_name='\u041a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u044f', to='adv.Communication')),
            ],
            options={
                'verbose_name': '\u043b\u043e\u0433 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438',
                'verbose_name_plural': '\u043b\u043e\u0433 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0439',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u0424\u0418\u041e', blank=True)),
                ('email', models.EmailField(max_length=100, verbose_name='\u042d\u043b\u0435\u043a\u0442\u0440\u043e\u043d\u043d\u0430\u044f \u043f\u043e\u0447\u0442\u0430', blank=True)),
                ('phone', models.CharField(max_length=100, null=True, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d', blank=True)),
                ('primary_contact', models.BooleanField(default=False, verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u043a\u043e\u043d\u0442\u0430\u043a\u0442?')),
                ('client', models.ForeignKey(verbose_name='\u041a\u043b\u0438\u0435\u043d\u0442', to='adv.Client')),
            ],
            options={
                'verbose_name': '\u043a\u043e\u043d\u0442\u0430\u043a\u0442',
                'verbose_name_plural': '\u043a\u043e\u043d\u0442\u0430\u043a\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='Direct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('text', models.TextField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('url', models.URLField(null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True)),
                ('source', models.CharField(max_length=255, verbose_name='\u0421\u0430\u0439\u0442', blank=True)),
                ('pixel_audit', models.CharField(max_length=255, verbose_name='\u041a\u043e\u0434 \u0434\u043b\u044f \u043f\u0438\u043a\u0441\u0435\u043b\u044c-\u0430\u0443\u0434\u0438\u0442\u0430', blank=True)),
                ('url_mask', models.CharField(max_length=255, blank=True, help_text='\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: /tourism/baikal/, \u0432\u044b\u0432\u0435\u0434\u0435\u0442\u0441\u044f \u043d\u0430 \u0432\u0441\u0435\u0445 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430\u0445, \u043d\u0430\u0447\u0438\u043d\u0430\u044e\u0449\u0438\u0445\u0441\u044f \u0441 \u044d\u0442\u043e\u0439 \u0441\u0441\u044b\u043b\u043a\u0438', null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u0434\u043b\u044f \u0432\u044b\u0432\u043e\u0434\u0430', db_index=True)),
                ('client', models.ForeignKey(verbose_name='\u041a\u043b\u0438\u0435\u043d\u0442', to='adv.Client')),
                ('site', models.ForeignKey(verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', blank=True, to='options.Site', null=True)),
            ],
            options={
                'verbose_name': '\u0422\u0435\u043a\u0441\u0442\u043e\u0432\u0430\u044f \u0440\u0435\u043a\u043b\u0430\u043c\u0430',
                'verbose_name_plural': '\u0422\u0435\u043a\u0441\u0442\u043e\u0432\u0430\u044f \u0440\u0435\u043a\u043b\u0430\u043c\u0430',
            },
        ),
        migrations.CreateModel(
            name='DirectPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_from', models.DateField(verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e', db_index=True)),
                ('date_to', models.DateField(verbose_name='\u041a\u043e\u043d\u0435\u0446', db_index=True)),
                ('direct', models.ForeignKey(to='adv.Direct')),
            ],
            options={
                'db_table': 'adv_direct_period',
                'verbose_name': '\u043f\u0435\u0440\u0438\u043e\u0434 \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f',
                'verbose_name_plural': '\u043f\u0435\u0440\u0438\u043e\u0434 \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('main', irk.utils.fields.file.FileRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0411\u0430\u043d\u043d\u0435\u0440', blank=True)),
                ('main_768', irk.utils.fields.file.FileRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0411\u0430\u043d\u043d\u0435\u0440 \u0434\u043b\u044f \u0448\u0438\u0440\u0438\u043d\u044b 768', blank=True)),
                ('main_420', irk.utils.fields.file.FileRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0411\u0430\u043d\u043d\u0435\u0440 \u0434\u043b\u044f \u0448\u0438\u0440\u0438\u043d\u044b 420', blank=True)),
                ('main_320', irk.utils.fields.file.FileRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0411\u0430\u043d\u043d\u0435\u0440 \u0434\u043b\u044f \u0448\u0438\u0440\u0438\u043d\u044b 320', blank=True)),
                ('dummy', irk.utils.fields.file.ImageRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0417\u0430\u0433\u043b\u0443\u0448\u043a\u0430', blank=True)),
                ('video', irk.utils.fields.file.FileRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0412\u0438\u0434\u0435\u043e (mp4)', blank=True)),
                ('video_ogg', irk.utils.fields.file.FileRemovableField(upload_to=irk.adv.models.get_upload_to_path, null=True, verbose_name='\u0412\u0438\u0434\u0435\u043e (ogg)', blank=True)),
                ('bgimage', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/adv/banners/', null=True, verbose_name='\u0444\u043e\u043d (\u043b\u0435\u0432.)', blank=True)),
                ('bgimage2', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/adv/banners/', null=True, verbose_name='\u0444\u043e\u043d (\u043f\u0440\u0430\u0432.)', blank=True)),
                ('bgcolor', irk.utils.db.models.fields.color.ColorField(help_text='\u0412 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 #13bf99', max_length=6, null=True, verbose_name='\u0426\u0432\u0435\u0442 \u0444\u043e\u043d\u0430', blank=True)),
                ('url', models.URLField(null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True)),
                ('alt', models.CharField(max_length=255, null=True, verbose_name=b'alt', blank=True)),
                ('deleted', models.BooleanField(default=False, verbose_name='\u0423\u0434\u0430\u043b\u0438\u0442\u044c')),
                ('text', models.CharField(max_length=300, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442', blank=True)),
                ('html5_url', models.URLField(verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 html5 \u0431\u0430\u043d\u043d\u0435\u0440', blank=True)),
                ('html5_code', models.TextField(verbose_name='html5 \u043a\u043e\u0434', blank=True)),
                ('html5', irk.utils.fields.file.FileArchiveField(upload_to=irk.adv.models.upload_html5_file, null=True, verbose_name='\u0411\u0430\u043d\u043d\u0435\u0440 html5', blank=True)),
                ('banner', models.ForeignKey(to='adv.Banner')),
            ],
            options={
                'verbose_name': '\u0444\u0430\u0439\u043b\u044b',
                'verbose_name_plural': '\u0444\u0430\u0439\u043b\u044b',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('banner', models.ForeignKey(to='adv.Banner')),
                ('site', models.ForeignKey(verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', blank=True, to='options.Site', null=True)),
            ],
            options={
                'verbose_name': '\u0440\u0430\u0441\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0440\u0430\u0441\u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, '\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440'), (2, '\u041f\u0435\u0440\u0435\u0445\u043e\u0434'), (3, '\u0414\u043e\u0441\u043a\u0440\u043e\u043b\u043b')])),
                ('date', models.DateField(verbose_name='\u0414\u0430\u0442\u0430')),
                ('cnt', models.PositiveIntegerField()),
                ('banner', models.ForeignKey(verbose_name='\u0411\u0430\u043d\u043d\u0435\u0440', to='adv.Banner')),
                ('file', models.ForeignKey(to='adv.File', null=True)),
                ('site', models.ForeignKey(verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b', blank=True, to='options.Site', null=True)),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043f\u0438\u0441\u044c',
                'verbose_name_plural': '\u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430',
            },
        ),
        migrations.CreateModel(
            name='MailHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u043e\u0442\u043f\u0440\u0430\u0432\u043a\u0438')),
                ('title', models.CharField(max_length=500, verbose_name='\u0422\u0435\u043c\u0430')),
                ('text', models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
            ],
            options={
                'verbose_name': '\u043f\u043e\u0447\u0442\u043e\u0432\u0430\u044f \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0430',
                'verbose_name_plural': '\u043f\u043e\u0447\u0442\u043e\u0432\u044b\u0435 \u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='MailHistory_Recipients',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_sent', models.NullBooleanField(default=False)),
                ('contact', models.ForeignKey(to='adv.Contact')),
            ],
            options={
                'verbose_name': '\u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0430 \u043f\u043e \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0430\u043c',
                'verbose_name_plural': '\u0440\u0430\u0441\u0441\u044b\u043b\u043a\u0438 \u043f\u043e \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0430\u043c',
            },
        ),
        migrations.CreateModel(
            name='ManagerClientHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_action', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f')),
                ('action', models.ForeignKey(verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043d\u0430\u0434 \u043a\u043b\u0438\u0435\u043d\u0442\u043e\u043c', to='adv.Action')),
                ('client', models.ForeignKey(verbose_name='\u041a\u043b\u0438\u0435\u043d\u0442', to='adv.Client')),
            ],
            options={
                'verbose_name': '\u043b\u043e\u0433 \u0440\u0430\u0431\u043e\u0442\u044b \u0441 \u043a\u043b\u0438\u0435\u043d\u043e\u043c',
                'verbose_name_plural': '\u043b\u043e\u0433 \u0440\u0430\u0431\u043e\u0442\u044b \u0441 \u043a\u043b\u0438\u0435\u043d\u0430\u043c\u0438',
            },
        ),
        migrations.CreateModel(
            name='Net',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField(default=0, verbose_name='\u0421\u0443\u043c\u043c\u0430 \u043f\u043b\u0430\u0442\u0435\u0436\u0430')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043b\u0430\u0442\u0435\u0436\u0430')),
                ('booking', models.ForeignKey(verbose_name='\u0411\u0440\u043e\u043d\u044c', to='adv.Booking')),
            ],
            options={
                'verbose_name': '\u043e\u043f\u043b\u0430\u0442\u0430',
                'verbose_name_plural': '\u043e\u043f\u043b\u0430\u0442\u0430',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_from', models.DateField(verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e', db_index=True)),
                ('date_to', models.DateField(verbose_name='\u041a\u043e\u043d\u0435\u0446', db_index=True)),
                ('show_time_start', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u043a\u0430\u0437\u0430 \u0441', null=True, editable=False, blank=True)),
                ('show_time_end', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043f\u043e\u043a\u0430\u0437\u0430 \u043f\u043e', null=True, editable=False, blank=True)),
                ('banner', models.ForeignKey(to='adv.Banner')),
            ],
            options={
                'verbose_name': '\u043f\u0435\u0440\u0438\u043e\u0434 \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f',
                'verbose_name_plural': '\u043f\u0435\u0440\u0438\u043e\u0434 \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField(default=0, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f')),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('show_text', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0442\u0435\u043a\u0441\u0442 \u043f\u043e\u0434 \u0431\u0430\u043d\u043d\u0435\u0440\u043e\u043c')),
                ('visible', models.BooleanField(default=True, verbose_name='\u0421\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0435\u0435 \u043c\u0435\u0441\u0442\u043e')),
                ('dayPrice', models.FloatField(default=0.0, verbose_name='\u0426\u0435\u043d\u0430 \u0437\u0430 \u0434\u0435\u043d\u044c \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f')),
                ('booking_visible', models.BooleanField(default=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u0432 \u0430\u0434\u0440\u0435\u0441\u043a\u0435')),
                ('empty_notif', models.BooleanField(default=False, verbose_name='\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u044f\u0442\u044c \u043e \u043f\u0440\u043e\u0441\u0442\u043e\u0435')),
                ('juridical_required', models.BooleanField(default=False, help_text='\u0414\u043e\u043f. \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u043a\u043b\u0438\u0435\u043d\u0442\u0435, \u0432\u044b\u0432\u043e\u0434\u044f\u0449\u0430\u044f\u0441\u044f \u043d\u0430 \u0441\u0430\u0439\u0442\u0435', verbose_name='\u0422\u0440\u0435\u0431\u043e\u0432\u0430\u0442\u044c \u044e\u0440\u0438\u0434\u0438\u0447\u0435\u0441\u043a\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u043b\u0438\u0435\u043d\u0442\u0430')),
                ('about_price', models.OneToOneField(related_name='adv_place', null=True, blank=True, to='about.Price', verbose_name='\u041f\u0440\u0430\u0439\u0441')),
                ('site', models.ForeignKey(verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b \u0441\u0430\u0439\u0442\u0430', blank=True, to='options.Site', null=True)),
            ],
            options={
                'verbose_name': '\u043c\u0435\u0441\u0442\u043e \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f',
                'verbose_name_plural': '\u043c\u0435\u0441\u0442\u0430 \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='SMTPErrors',
            fields=[
                ('code', models.PositiveIntegerField(serialize=False, verbose_name='\u041a\u043e\u0434 \u043e\u0448\u0438\u0431\u043a\u0438', primary_key=True)),
                ('definition', models.TextField(default=b'', verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('type', models.CharField(max_length=255, null=True, verbose_name='\u0422\u0438\u043f', choices=[('2XX', '\u041a\u043e\u043c\u0430\u043d\u0434\u0430 \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0430'), ('3XX', '\u041e\u0436\u0438\u0434\u0430\u044e\u0442\u0441\u044f \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u043e\u0442 \u043a\u043b\u0438\u0435\u043d\u0442\u0430'), ('4XX', '\u0412\u0440\u0435\u043c\u0435\u043d\u043d\u0430\u044f \u043e\u0448\u0438\u0431\u043a\u0430, \u043a\u043b\u0438\u0435\u043d\u0442 \u0434\u043e\u043b\u0436\u0435\u043d \u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0441\u0442\u0438 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0443\u044e \u043f\u043e\u043f\u044b\u0442\u043a\u0443 \u0447\u0435\u0440\u0435\u0437 \u043d\u0435\u043a\u043e\u0442\u043e\u0440\u043e\u0435 \u0432\u0440\u0435\u043c\u044f'), ('5XX', '\u041d\u0435\u0443\u0441\u0442\u0440\u0430\u043d\u0438\u043c\u0430\u044f \u043e\u0448\u0438\u0431\u043a\u0430')])),
            ],
            options={
                'verbose_name': '\u043e\u0448\u0438\u0431\u043a\u0430 SMTP \u0441\u0435\u0440\u0432\u0435\u0440\u0430',
                'verbose_name_plural': '\u043e\u0448\u0438\u0431\u043a\u0438 SMTP \u0441\u0435\u0440\u0432\u0435\u0440\u0430',
            },
        ),
        migrations.CreateModel(
            name='Targetix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('code', models.TextField(verbose_name='\u041a\u043e\u0434')),
            ],
            options={
                'verbose_name': '\u0412\u043d\u0435\u0448\u043d\u0438\u0439 \u0431\u0430\u043d\u043d\u0435\u0440',
                'verbose_name_plural': '\u0412\u043d\u0435\u0448\u043d\u0438\u0435 \u0431\u0430\u043d\u043d\u0435\u0440\u044b',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('file', models.CharField(max_length=255)),
                ('place', models.ForeignKey(to='adv.Place')),
            ],
        ),
        migrations.CreateModel(
            name='TypeOfCommunication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100, verbose_name='\u0422\u0438\u043f \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438')),
            ],
            options={
                'verbose_name': '\u0442\u0438\u043f \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438',
                'verbose_name_plural': '\u0442\u0438\u043f\u044b \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0439',
            },
        ),
        migrations.CreateModel(
            name='UserOption',
            fields=[
                ('user', irk.utils.fields.onetoone.AutoOneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c')),
                ('color', models.CharField(default=irk.adv.models.random_color, max_length=7, null=True, verbose_name='\u0426\u0432\u0435\u0442', blank=True)),
                ('show_done_duties', models.BooleanField(default=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u043d\u044b\u0435 \u0434\u0435\u043b\u0430')),
            ],
            options={
                'verbose_name': '\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439 CRM',
                'verbose_name_plural': '\u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439 CRM',
            },
        ),
        migrations.AddField(
            model_name='place',
            name='targetix',
            field=models.ForeignKey(blank=True, to='adv.Targetix', null=True),
        ),
        migrations.AddField(
            model_name='managerclienthistory',
            name='user',
            field=models.ForeignKey(default=None, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='mailhistory_recipients',
            name='error_code',
            field=models.ForeignKey(default=None, blank=True, to='adv.SMTPErrors', null=True),
        ),
        migrations.AddField(
            model_name='mailhistory_recipients',
            name='mailhistory',
            field=models.ForeignKey(to='adv.MailHistory'),
        ),
        migrations.AddField(
            model_name='mailhistory',
            name='manager',
            field=models.ForeignKey(verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mailhistory',
            name='recipients',
            field=models.ManyToManyField(to='adv.Contact', verbose_name='\u041f\u043e\u043b\u0443\u0447\u0430\u0442\u0435\u043b\u0438', through='adv.MailHistory_Recipients'),
        ),
        migrations.AddField(
            model_name='location',
            name='template',
            field=models.ForeignKey(verbose_name='\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430', blank=True, to='adv.Template', null=True),
        ),
        migrations.AddField(
            model_name='communicationhistory',
            name='user',
            field=models.ForeignKey(verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='communication',
            name='contact',
            field=models.ForeignKey(verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u043e\u0435 \u043b\u0438\u0446\u043e', blank=True, to='adv.Contact', null=True),
        ),
        migrations.AddField(
            model_name='communication',
            name='mail_msg',
            field=models.ForeignKey(verbose_name='\u041f\u0438\u0441\u044c\u043c\u043e', blank=True, to='adv.MailHistory', null=True),
        ),
        migrations.AddField(
            model_name='communication',
            name='manager',
            field=models.ForeignKey(verbose_name='\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='communication',
            name='type',
            field=models.ForeignKey(verbose_name='\u0422\u0438\u043f \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438', to='adv.TypeOfCommunication'),
        ),
        migrations.AddField(
            model_name='client',
            name='manager',
            field=models.ForeignKey(verbose_name='\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='type',
            field=models.ForeignKey(verbose_name='\u0422\u0438\u043f', blank=True, to='adv.ClientType', null=True),
        ),
        migrations.AddField(
            model_name='bookinghistory',
            name='user',
            field=models.ForeignKey(verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='booking',
            name='client',
            field=models.ForeignKey(verbose_name='\u041a\u043b\u0438\u0435\u043d\u0442', to='adv.Client'),
        ),
        migrations.AddField(
            model_name='booking',
            name='place',
            field=models.ForeignKey(verbose_name='\u041c\u0435\u0441\u0442\u043e \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f', to='adv.Place'),
        ),
        migrations.AddField(
            model_name='banner',
            name='client',
            field=models.ForeignKey(verbose_name='\u041a\u043b\u0438\u0435\u043d\u0442', to='adv.Client'),
        ),
        migrations.AddField(
            model_name='banner',
            name='place',
            field=models.ForeignKey(blank=True, editable=False, to='adv.Place', null=True, verbose_name='\u041c\u0435\u0441\u0442\u043e'),
        ),
        migrations.AddField(
            model_name='banner',
            name='places',
            field=models.ManyToManyField(related_name='banners', verbose_name='\u041c\u0435\u0441\u0442\u0430 \u0440\u0430\u0437\u043c\u0435\u0449\u0435\u043d\u0438\u044f', to='adv.Place'),
        ),
    ]
