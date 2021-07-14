# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.utils.db.models
import irk.utils.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('firms_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='phones.Firms')),
                ('is_active', models.BooleanField(default=True)),
                ('name_add', models.TextField(help_text='\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d HTML', verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('name_short', models.CharField(max_length=765, verbose_name='\u041a\u043e\u0440\u043e\u0442\u043a\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('phone_main', models.CharField(max_length=765, verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0442\u0435\u043b\u0435\u0444\u043e\u043d', blank=True)),
                ('contact', models.CharField(max_length=765, verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u043e\u0435 \u043b\u0438\u0446\u043e', blank=True)),
                ('sia_id', models.PositiveIntegerField(default=0, verbose_name='ID \u0431\u0430\u043d\u043a\u0430 \u0432 SIA')),
                ('money_limit', models.BooleanField(default=False, verbose_name='\u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435 \u043f\u043e \u043e\u0431\u043c\u0435\u043d\u0443 \u0432\u0430\u043b\u044e\u0442\u044b')),
                ('have_usd', models.BooleanField(default=True, verbose_name='\u0415\u0441\u0442\u044c USD')),
                ('have_euro', models.BooleanField(default=True, verbose_name='\u0415\u0441\u0442\u044c Euro')),
                ('have_cny', models.BooleanField(default=True, verbose_name='\u0415\u0441\u0442\u044c CNY')),
                ('on_main', models.BooleanField(default=False, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u0443\u044e')),
                ('list_image', irk.utils.fields.file.ImageRemovableField(upload_to=b'img/site/currency/bank/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f \u0434\u043b\u044f \u0441\u043f\u0438\u0441\u043a\u0430', blank=True)),
                ('credit_mortgage', models.BooleanField(default=False, verbose_name='\u0418\u043f\u043e\u0442\u0435\u0447\u043d\u044b\u0439 \u043a\u0440\u0435\u0434\u0438\u0442')),
                ('credit_deposit', models.BooleanField(default=False, verbose_name='\u0414\u0435\u043f\u043e\u0437\u0438\u0442')),
                ('credit_auto', models.BooleanField(default=False, verbose_name='\u0410\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0439 \u043a\u0440\u0435\u0434\u0438\u0442')),
                ('credit_consumer', models.BooleanField(default=False, verbose_name='\u041f\u043e\u0442\u0440\u0435\u0431\u0438\u0442\u0435\u043b\u044c\u0441\u043a\u0438\u0439 \u043a\u0440\u0435\u0434\u0438\u0442')),
                ('credit_encash', models.BooleanField(default=False, verbose_name='\u041a\u0440\u0435\u0434\u0438\u0442 \u043d\u0430\u043b\u0438\u0447\u043d\u044b\u043c\u0438')),
                ('grabber', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'currency_banks',
                'verbose_name': '\u0431\u0430\u043d\u043a',
                'verbose_name_plural': '\u0431\u0430\u043d\u043a\u0438',
            },
            bases=('phones.firms',),
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b')),
                ('guarantee', models.TextField(verbose_name='\u041e\u0431\u0435\u0441\u043f\u0435\u0447\u0435\u043d\u0438\u0435 \u043a\u0440\u0435\u0434\u0438\u0442\u0430')),
                ('requirements', models.TextField(verbose_name='\u0422\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u043f\u043e \u0441\u0442\u0440\u0430\u0445\u043e\u0432\u0430\u043d\u0438\u044e')),
                ('paying', models.TextField(verbose_name='\u041f\u043e\u0433\u0430\u0448\u0435\u043d\u0438\u0435 \u043a\u0440\u0435\u0434\u0438\u0442\u0430')),
                ('early_paying', models.TextField(verbose_name='\u0414\u043e\u0441\u0440\u043e\u0447\u043d\u043e\u0435 \u043f\u043e\u0433\u0430\u0448\u0435\u043d\u0438\u0435 \u043a\u0440\u0435\u0434\u0438\u0442\u0430')),
                ('borrower_requirements', models.TextField(verbose_name='\u0422\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f \u043a \u0437\u0430\u0435\u043c\u0449\u0438\u043a\u0443')),
                ('additional_info', models.TextField(verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043f\u043e \u043a\u0440\u0435\u0434\u0438\u0442\u0443', blank=True)),
                ('time', models.CharField(max_length=50, verbose_name='\u0421\u0440\u043e\u043a \u0440\u0430\u0441\u0441\u043c\u043e\u0442\u0440\u0435\u043d\u0438\u044f')),
                ('additional', models.TextField(verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f', blank=True)),
                ('rates', models.TextField(verbose_name='\u0421\u0442\u0430\u0432\u043a\u0438 \u043f\u043e \u043a\u0440\u0435\u0434\u0438\u0442\u0443')),
                ('updated', models.DateField(verbose_name='\u0414\u0430\u0442\u0430 \u0430\u043a\u0442\u0443\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u0438')),
            ],
            options={
                'db_table': 'currency_credits',
                'verbose_name': '\u043a\u0440\u0435\u0434\u0438\u0442',
                'verbose_name_plural': '\u043a\u0440\u0435\u0434\u0438\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='CurrencyCbrf',
            fields=[
                ('stamp', models.DateField(serialize=False, primary_key=True)),
                ('usd', models.FloatField(verbose_name='\u041a\u0443\u0440\u0441 \u0434\u043e\u043b\u043b\u0430\u0440\u0430 \u0421\u0428\u0410', blank=True)),
                ('euro', models.FloatField(verbose_name='\u041a\u0443\u0440\u0441 \u0435\u0432\u0440\u043e', db_column=b'euro', blank=True)),
                ('cny', models.FloatField(verbose_name='\u041a\u0443\u0440\u0441 \u044e\u0430\u043d\u044f', blank=True)),
                ('visible', models.BooleanField(default=False, db_index=True, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c')),
            ],
            options={
                'db_table': 'currency_base',
                'verbose_name': '\u043a\u0443\u0440\u0441 \u0426\u0411 \u0420\u0424',
                'verbose_name_plural': '\u043a\u0443\u0440\u0441\u044b \u0426\u0411 \u0420\u0424',
            },
            bases=(irk.utils.db.models.Loggable, models.Model),
        ),
        migrations.CreateModel(
            name='CurrencyRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stamp', models.DateField(db_index=True)),
                ('usd_buy', models.FloatField(null=True, verbose_name='USD \u043f\u043e\u043a\u0443\u043f\u043a\u0430', db_column=b'usdBuy')),
                ('usd_sell', models.FloatField(null=True, verbose_name='USD \u043f\u0440\u043e\u0434\u0430\u0436\u0430', db_column=b'usdSell')),
                ('euro_buy', models.FloatField(null=True, verbose_name='EUR \u043f\u043e\u043a\u0443\u043f\u043a\u0430', db_column=b'euroBuy')),
                ('euro_sell', models.FloatField(null=True, verbose_name='EUR \u043f\u0440\u043e\u0434\u0430\u0436\u0430', db_column=b'euroSell')),
                ('cny_buy', models.FloatField(null=True, verbose_name='CNY \u043f\u043e\u043a\u0443\u043f\u043a\u0430', db_column=b'cnyBuy', blank=True)),
                ('cny_sell', models.FloatField(null=True, verbose_name='CNY \u043f\u0440\u043e\u0434\u0430\u0436\u0430', db_column=b'cnySell', blank=True)),
                ('time', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f', blank=True)),
            ],
            options={
                'db_table': 'currency_rates',
                'verbose_name': '\u043a\u0443\u0440\u0441 \u0432\u0430\u043b\u044e\u0442',
                'verbose_name_plural': '\u043a\u0443\u0440\u0441\u044b \u0432\u0430\u043b\u044e\u0442',
            },
            bases=(irk.utils.db.models.Loggable, models.Model),
        ),
        migrations.CreateModel(
            name='CurrencyRateLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stamp', models.DateField(db_index=True)),
                ('usd_buy', models.FloatField(null=True, verbose_name='USD \u043f\u043e\u043a\u0443\u043f\u043a\u0430')),
                ('usd_sell', models.FloatField(null=True, verbose_name='USD \u043f\u0440\u043e\u0434\u0430\u0436\u0430')),
                ('euro_buy', models.FloatField(null=True, verbose_name='EUR \u043f\u043e\u043a\u0443\u043f\u043a\u0430')),
                ('euro_sell', models.FloatField(null=True, verbose_name='EUR \u043f\u0440\u043e\u0434\u0430\u0436\u0430')),
                ('cny_buy', models.FloatField(null=True, verbose_name='CNY \u043f\u043e\u043a\u0443\u043f\u043a\u0430', blank=True)),
                ('cny_sell', models.FloatField(null=True, verbose_name='CNY \u043f\u0440\u043e\u0434\u0430\u0436\u0430', blank=True)),
                ('time', models.TimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f')),
            ],
            options={
                'db_table': 'currency_rates_log',
                'verbose_name': '\u043b\u043e\u0433 \u043a\u0443\u0440\u0441\u0430 \u0432\u0430\u043b\u044e\u0442',
                'verbose_name_plural': '\u043b\u043e\u0433\u0438 \u043a\u0443\u0440\u0441\u0430 \u0432\u0430\u043b\u044e\u0442',
            },
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0432\u043a\u043b\u0430\u0434\u0430')),
                ('description', models.TextField(verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f', blank=True)),
                ('rate', models.TextField(verbose_name='\u0413\u043e\u0434\u043e\u0432\u044b\u0435 \u043f\u0440\u043e\u0446\u0435\u043d\u0442\u043d\u044b\u0435 \u0441\u0442\u0430\u0432\u043a\u0438')),
                ('date', models.TextField(verbose_name='\u0421\u0440\u043e\u043a \u0432\u043a\u043b\u0430\u0434\u0430')),
                ('currency', models.TextField(verbose_name='\u0412\u0430\u043b\u044e\u0442\u0430 \u0432\u043a\u043b\u0430\u0434\u0430')),
                ('amount_min', models.TextField(verbose_name='\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0443\u043c\u043c\u0430 \u0432\u043a\u043b\u0430\u0434\u0430', blank=True)),
                ('amount_max', models.TextField(verbose_name='\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0443\u043c\u043c\u0430 \u0432\u043a\u043b\u0430\u0434\u0430', blank=True)),
                ('payments', models.TextField(verbose_name='\u0423\u0441\u043b\u043e\u0432\u0438\u044f \u0432\u044b\u043f\u043b\u0430\u0442 \u043f\u0440\u043e\u0446\u0435\u043d\u0442\u043e\u0432', blank=True)),
                ('annulment', models.TextField(verbose_name='\u0423\u0441\u043b\u043e\u0432\u0438\u044f \u0434\u043e\u0441\u0440\u043e\u0447\u043d\u043e\u0433\u043e \u0440\u0430\u0441\u0442\u043e\u0440\u0436\u0435\u043d\u0438\u044f \u0434\u043e\u0433\u043e\u0432\u043e\u0440\u0430', blank=True)),
                ('additional', models.TextField(verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f', blank=True)),
            ],
            options={
                'db_table': 'currency_deposits',
                'verbose_name': '\u0432\u043a\u043b\u0430\u0434',
                'verbose_name_plural': '\u0432\u043a\u043b\u0430\u0434\u044b',
            },
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numeral_code', models.PositiveIntegerField(verbose_name='\u0427\u0438\u0441\u043b\u043e\u0432\u043e\u0439 \u043a\u043e\u0434')),
                ('code', models.CharField(unique=True, max_length=5, verbose_name='\u041a\u043e\u0434 \u0432\u0430\u043b\u044e\u0442\u044b')),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('nominal', models.PositiveIntegerField(verbose_name='\u041d\u043e\u043c\u0438\u043d\u0430\u043b')),
                ('value', models.FloatField(verbose_name='\u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435')),
            ],
            options={
                'db_table': 'currency_exchange_rates',
                'verbose_name': '\u043a\u0443\u0440\u0441 \u043e\u0431\u043c\u0435\u043d\u0430',
                'verbose_name_plural': '\u043a\u0443\u0440\u0441\u044b \u043e\u0431\u043c\u0435\u043d\u0430',
            },
        ),
    ]
