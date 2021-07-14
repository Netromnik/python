# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('obed', '0002_auto_20161212_1624'),
        ('afisha', '0002_auto_20161212_1624'),
        ('options', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('phones', '0002_bankproxy'),
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstablishmentProxy',
            fields=[
            ],
            options={
                'verbose_name': '\u041e\u0431\u0435\u0434: \u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435',
                'proxy': True,
                'verbose_name_plural': '\u041e\u0431\u0435\u0434: \u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f',
            },
            bases=('obed.establishment',),
        ),
        migrations.CreateModel(
            name='GuideProxy',
            fields=[
            ],
            options={
                'verbose_name': '\u0413\u0438\u0434',
                'proxy': True,
                'verbose_name_plural': '\u0413\u0438\u0434',
            },
            bases=('afisha.guide',),
        ),
        migrations.CreateModel(
            name='HotelProxy',
            fields=[
            ],
            options={
                'verbose_name': '\u0413\u043e\u0441\u0442\u0438\u043d\u0438\u0446\u0430',
                'proxy': True,
                'verbose_name_plural': '\u0422\u0443\u0440\u0438\u0437\u043c: \u0413\u043e\u0441\u0442\u0438\u043d\u0438\u0446\u044b',
            },
            bases=('tourism.hotel',),
        ),
        migrations.CreateModel(
            name='TourBaseProxy',
            fields=[
            ],
            options={
                'verbose_name': '\u0422\u0443\u0440\u0431\u0430\u0437\u0430',
                'proxy': True,
                'verbose_name_plural': '\u0422\u0443\u0440\u0438\u0437\u043c: \u0422\u0443\u0440\u0431\u0430\u0437\u044b',
            },
            bases=('tourism.tourbase',),
        ),
        migrations.CreateModel(
            name='TourFirmProxy',
            fields=[
            ],
            options={
                'verbose_name': '\u0422\u0443\u0440\u0444\u0438\u0440\u043c\u0430',
                'proxy': True,
                'verbose_name_plural': '\u0422\u0443\u0440\u0438\u0437\u043c: \u0422\u0443\u0440\u0444\u0438\u0440\u043c\u044b',
            },
            bases=('tourism.tourfirm',),
        ),
        migrations.AddField(
            model_name='worktime',
            name='address',
            field=models.ForeignKey(related_name='address_worktimes', verbose_name='\u0410\u0434\u0440\u0435\u0441', to='phones.Address'),
        ),
        migrations.AddField(
            model_name='vip',
            name='firm',
            field=models.ForeignKey(verbose_name='\u0424\u0438\u0440\u043c\u0430', to='phones.Firms'),
        ),
        migrations.AddField(
            model_name='sections',
            name='categories',
            field=models.ManyToManyField(to='phones.MetaSection', verbose_name='\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438', blank=True),
        ),
        migrations.AddField(
            model_name='sections',
            name='content_type',
            field=models.ForeignKey(verbose_name='\u0422\u0438\u043f', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='sections',
            name='parent',
            field=models.ForeignKey(related_name='children', db_column=b'parent', blank=True, to='phones.Sections', null=True, verbose_name=b'\xd0\xa0\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd1\x81\xd0\xba\xd0\xb0\xd1\x8f \xd1\x80\xd1\x83\xd0\xb1\xd1\x80\xd0\xb8\xd0\xba\xd0\xb0'),
        ),
        migrations.AddField(
            model_name='sections',
            name='sites',
            field=models.ManyToManyField(to='options.Site', verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b\u044b', blank=True),
        ),
        migrations.AddField(
            model_name='scanstore',
            name='firm',
            field=models.ForeignKey(verbose_name='\u0424\u0438\u0440\u043c\u0430', blank=True, to='phones.Firms', null=True),
        ),
        migrations.AddField(
            model_name='scanstore',
            name='ownership',
            field=models.ForeignKey(verbose_name='\u0422\u0438\u043f', blank=True, to='phones.Ownership', null=True),
        ),
        migrations.AddField(
            model_name='firms',
            name='content_type',
            field=models.ForeignKey(verbose_name='\u0422\u0438\u043f', blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='firms',
            name='ownership',
            field=models.ForeignKey(db_column=b'ownership', blank=True, to='phones.Ownership', null=True, verbose_name='\u0424\u043e\u0440\u043c\u0430 \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u043e\u0441\u0442\u0438'),
        ),
        migrations.AddField(
            model_name='firms',
            name='section',
            field=models.ManyToManyField(to='phones.Sections', verbose_name='\u0420\u0443\u0431\u0440\u0438\u043a\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='firms',
            name='user',
            field=models.ForeignKey(verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='firm',
            field=models.ForeignKey(to='phones.Firms'),
        ),
        migrations.AddField(
            model_name='address',
            name='city_id',
            field=models.ForeignKey(db_column=b'city_id', default=1, verbose_name='\u0413\u043e\u0440\u043e\u0434', to='map.Cities'),
        ),
        migrations.AddField(
            model_name='address',
            name='firm_id',
            field=models.ForeignKey(to='phones.Firms', db_column=b'firm_id'),
        ),
        migrations.AddField(
            model_name='address',
            name='streetid',
            field=models.ForeignKey(db_column=b'streetID', blank=True, to='map.Streets', null=True),
        ),
        migrations.CreateModel(
            name='GisFirm',
            fields=[
            ],
            options={
                'db_table': 'phones_firms',
                'verbose_name': '\u0413\u0440\u0430\u0431\u0431\u0435\u0440 \u0444\u0438\u0440\u043c',
                'proxy': True,
                'verbose_name_plural': '\u0413\u0440\u0430\u0431\u0431\u0435\u0440 \u0444\u0438\u0440\u043c',
            },
            bases=('phones.firms',),
        ),
        migrations.AlterUniqueTogether(
            name='worktime',
            unique_together=set([('address', 'weekday')]),
        ),
    ]
