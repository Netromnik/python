# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoice', '0001_initial'),
        ('afisha', '0020_eventtype_is_visible'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.FloatField(verbose_name='\u0421\u0443\u043c\u043c\u0430 \u0437\u0430\u043a\u0430\u0437\u0430')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0433\u043e \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0417\u0430\u043a\u0430\u0437',
                'verbose_name_plural': '\u0417\u0430\u043a\u0430\u0437\u044b',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='is_approved',
            field=models.BooleanField(default=False, verbose_name='\u041a\u043e\u043c\u0435\u0440\u0447\u0435\u0441\u043a\u043e\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043e\u0434\u043e\u0431\u0440\u0435\u043d\u043e'),
        ),
        migrations.AddField(
            model_name='event',
            name='is_commercial',
            field=models.BooleanField(default=False, verbose_name='\u041a\u043e\u043c\u0435\u0440\u0447\u0435\u0441\u043a\u043e\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0435'),
        ),
        migrations.AddField(
            model_name='event',
            name='organizer',
            field=models.CharField(default=b'', max_length=255, verbose_name='\u041e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0442\u043e\u0440', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='organizer_contacts',
            field=models.CharField(default=b'', max_length=1024, verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0442\u043e\u0440\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='organizer_email',
            field=models.EmailField(default=b'', max_length=254, verbose_name='E-mail \u043e\u0440\u0433\u0430\u043d\u0438\u0437\u0430\u0442\u043e\u0440\u0430', blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='event',
            field=models.ForeignKey(related_name='order_event', verbose_name='\u0421\u043e\u0431\u044b\u0442\u0438\u0435', to='afisha.Event'),
        ),
        migrations.AddField(
            model_name='order',
            name='invoice',
            field=models.OneToOneField(related_name='order_invoice', null=True, verbose_name='\u041f\u043b\u0430\u0442\u0435\u0436', to='invoice.Invoice'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(default=None, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
