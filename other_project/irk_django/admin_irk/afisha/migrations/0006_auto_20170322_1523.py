# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0005_auto_20170220_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='KinomaxBuilding',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True)),
                ('token', models.CharField(max_length=255, verbose_name='\u0442\u043e\u043a\u0435\u043d')),
                ('title', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('guide', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Guide', verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0433\u0438\u0434\u0430')),
            ],
            options={
                'verbose_name': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0432 kinomax',
                'verbose_name_plural': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f \u0432 kinomax',
            },
        ),
        migrations.CreateModel(
            name='KinomaxEvent',
            fields=[
                ('date_start', models.DateTimeField(null=True, verbose_name='\u0434\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('duration', models.IntegerField(null=True, verbose_name='\u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c (\u0441\u0435\u043a)')),
                ('rating', models.FloatField(null=True, verbose_name='\u0440\u0435\u0439\u0442\u0438\u043d\u0433 \u0432 \u0431\u0430\u043b\u043b\u0430\u0445')),
                ('votes', models.IntegerField(null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0433\u043e\u043b\u043e\u0441\u043e\u0432')),
                ('description', models.TextField(verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('director', models.CharField(max_length=255, verbose_name='\u0440\u0435\u0436\u0438\u0441\u0435\u0440')),
                ('cast', models.CharField(max_length=255, verbose_name='\u0430\u043a\u0442\u0435\u0440\u044b')),
                ('trailer', models.URLField(verbose_name='\u0442\u0440\u0435\u0439\u043b\u0435\u0440')),
                ('image', models.URLField(verbose_name='\u0430\u0434\u0440\u0435\u0441 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f')),
                ('genres', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'verbose_name': '\u0441\u043e\u0431\u044b\u0442\u0438\u0435 \u0432 kinomax',
                'verbose_name_plural': '\u0441\u043e\u0431\u044b\u0442\u0438\u044f \u0432 kinomax',
            },
        ),
        migrations.CreateModel(
            name='KinomaxHall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('title', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('building', models.ForeignKey(related_name='halls', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='afisha.KinomaxBuilding', null=True)),
                ('hall', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Hall', verbose_name='\u0437\u0430\u043b')),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043b \u0432 kinomax',
                'verbose_name_plural': '\u0437\u0430\u043b\u044b \u0432 kinomax',
            },
        ),
        migrations.CreateModel(
            name='KinomaxSession',
            fields=[
                ('datetime', models.DateTimeField(null=True, verbose_name='\u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f', db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('is_ignore', models.BooleanField(default=False, db_index=True, verbose_name='\u0438\u0433\u043d\u043e\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c')),
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True)),
                ('price', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('type', models.CharField(max_length=255, verbose_name='\u0442\u0438\u043f \u0441\u0435\u0430\u043d\u0441\u0430')),
                ('is_passed', models.BooleanField(default=False, db_index=True, verbose_name='\u0437\u0430\u043a\u043e\u043d\u0447\u0438\u043b\u0441\u044f')),
                ('current_session', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.CurrentSession', verbose_name='\u0441\u0435\u0430\u043d\u0441')),
                ('event', models.ForeignKey(related_name='sessions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435', to='afisha.KinomaxEvent', null=True)),
                ('hall', models.ForeignKey(related_name='sessions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0437\u0430\u043b', to='afisha.KinomaxHall', null=True)),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'datetime',
                'verbose_name': '\u0441\u0435\u0430\u043d\u0441 \u0432 kinomax',
                'verbose_name_plural': '\u0441\u0435\u0430\u043d\u0441\u044b \u0432 kinomax',
            },
        ),
        migrations.CreateModel(
            name='RamblerBuilding',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('address', models.CharField(max_length=255, verbose_name='\u0430\u0434\u0440\u0435\u0441')),
                ('latitude', models.FloatField(verbose_name='\u0448\u0438\u0440\u043e\u0442\u0430')),
                ('longitude', models.FloatField(verbose_name='\u0434\u043e\u043b\u0433\u043e\u0442\u0430')),
                ('rate', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=100, verbose_name='\u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f')),
                ('sale_from', models.CharField(max_length=50)),
                ('sale_for', models.CharField(max_length=50)),
                ('cancel_type', models.CharField(max_length=100)),
                ('cancel_period', models.IntegerField(null=True)),
                ('is_vvv_enabled', models.BooleanField()),
                ('has_terminal', models.BooleanField(verbose_name='\u0435\u0441\u0442\u044c \u0442\u0435\u0440\u043c\u0438\u043d\u0430\u043b')),
                ('has_print_device', models.BooleanField(verbose_name='\u0435\u0441\u0442\u044c \u043f\u0440\u0438\u043d\u0442\u0435\u0440')),
                ('class_type', models.CharField(max_length=30, verbose_name='\u0442\u0438\u043f')),
                ('city_id', models.IntegerField(verbose_name='id \u0433\u043e\u0440\u043e\u0434\u0430')),
                ('guide', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Guide', verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0433\u0438\u0434\u0430')),
            ],
            options={
                'verbose_name': '\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 Rambler.Kassa',
                'verbose_name_plural': '\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u044f Rambler.Kassa',
            },
        ),
        migrations.CreateModel(
            name='RamblerEvent',
            fields=[
                ('date_start', models.DateTimeField(null=True, verbose_name='\u0434\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('original_name', models.CharField(max_length=255, verbose_name='\u043e\u0440\u0438\u0433\u0438\u043d\u0430\u043b\u044c\u043d\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('genre', models.CharField(max_length=50, verbose_name='\u0436\u0430\u043d\u0440')),
                ('country', models.CharField(max_length=100, verbose_name='\u0441\u0442\u0440\u0430\u043d\u0430')),
                ('view_count_daily', models.IntegerField(null=True)),
                ('age_restriction', models.CharField(max_length=5, verbose_name='\u0432\u043e\u0437\u0440\u0430\u0441\u0442\u043d\u043e\u0435 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435')),
                ('thumbnail', models.CharField(max_length=255, verbose_name='\u043c\u0438\u043d\u0438\u0430\u0442\u044e\u0440\u0430')),
                ('horizonal_thumbnail', models.CharField(max_length=255, verbose_name='\u0433\u043e\u0440\u0438\u0437\u043e\u043d\u0442\u0430\u043b\u044c\u043d\u0430\u044f \u043c\u0438\u043d\u0438\u0430\u0442\u044e\u0440\u0430')),
                ('cast', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255, verbose_name='\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('director', models.CharField(max_length=100, verbose_name='\u0440\u0435\u0436\u0438\u0441\u0435\u0440')),
                ('creator_name', models.CharField(max_length=100, verbose_name='\u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e')),
                ('creator_id', models.CharField(max_length=5, verbose_name='id \u043f\u0440\u043e\u0438\u0437\u043e\u0432\u0434\u0438\u0442\u0435\u043b\u044f')),
                ('year', models.CharField(max_length=4, verbose_name='\u0433\u043e\u0434')),
                ('duration', models.CharField(max_length=10, verbose_name='\u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c')),
                ('is_non_stop', models.NullBooleanField(default=None)),
                ('rating', models.CharField(max_length=10, verbose_name='\u0440\u0435\u0439\u0442\u0438\u043d\u0433')),
                ('class_type', models.CharField(max_length=30, verbose_name='\u0442\u0438\u043f')),
            ],
            options={
                'verbose_name': '\u0421\u043e\u0431\u044b\u0442\u0438\u0435 \u0432 Rambler.Kassa',
                'verbose_name_plural': '\u0421\u043e\u0431\u044b\u0442\u0438\u044f \u0432 Rambler.Kassa',
            },
        ),
        migrations.CreateModel(
            name='RamblerHall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('hallid', models.CharField(max_length=10, verbose_name='hall id', db_index=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('building', models.ForeignKey(related_name='halls', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='afisha.RamblerBuilding', null=True)),
                ('hall', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Hall', verbose_name='\u0437\u0430\u043b')),
            ],
            options={
                'verbose_name': '\u0417\u0430\u043b \u0432 Rambler.Kassa',
                'verbose_name_plural': '\u0417\u0430\u043b\u044b \u0432 Rambler.Kassa',
            },
        ),
        migrations.CreateModel(
            name='RamblerSession',
            fields=[
                ('datetime', models.DateTimeField(null=True, verbose_name='\u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f', db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0441\u043e\u0437\u0434\u0430\u043d\u043e')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0438\u0437\u043c\u0435\u043d\u0435\u043d\u043e')),
                ('is_ignore', models.BooleanField(default=False, db_index=True, verbose_name='\u0438\u0433\u043d\u043e\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c')),
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True)),
                ('city_id', models.IntegerField(null=True, verbose_name='id \u0433\u043e\u0440\u043e\u0434\u0430')),
                ('creation_class_type', models.CharField(max_length=30, verbose_name='\u0442\u0438\u043f \u043f\u0440\u043e\u0438\u0437\u0432\u0435\u0434\u0435\u043d\u0438\u044f')),
                ('place_class_type', models.CharField(max_length=30, verbose_name='\u0442\u0438\u043f \u043c\u0435\u0441\u0442\u0430')),
                ('place_id', models.IntegerField(null=True, verbose_name='id \u043c\u0435\u0441\u0442\u0430', db_index=True)),
                ('format', models.CharField(max_length=50, verbose_name='\u0444\u043e\u0440\u043c\u0430\u0442')),
                ('is_sale_available', models.BooleanField(default=True, verbose_name='\u043f\u0440\u043e\u0434\u0430\u0436\u0430')),
                ('is_reservation_available', models.BooleanField(default=True, verbose_name='\u0431\u0440\u043e\u043d\u044c')),
                ('is_without_seats', models.BooleanField(default=False, verbose_name='\u0431\u0435\u0437 \u043c\u0435\u0441\u0442')),
                ('min_price', models.IntegerField(null=True, verbose_name='\u043c\u0438\u043d \u0446\u0435\u043d\u0430')),
                ('max_price', models.IntegerField(null=True, verbose_name='\u043c\u0430\u043a\u0441 \u0446\u0435\u043d\u0430')),
                ('hall_name', models.CharField(max_length=50, verbose_name='\u0437\u0430\u043b')),
                ('fee_type', models.CharField(max_length=50, verbose_name='\u0442\u0438\u043f \u0441\u0431\u043e\u0440\u0430')),
                ('fee_value', models.CharField(max_length=10, verbose_name='\u0441\u0431\u043e\u0440')),
                ('current_session', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.CurrentSession', verbose_name='\u0441\u0435\u0430\u043d\u0441')),
                ('event', models.ForeignKey(related_name='sessions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435', to='afisha.RamblerEvent', null=True)),
                ('hall', models.ForeignKey(related_name='sessions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0437\u0430\u043b', to='afisha.RamblerHall', null=True)),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'datetime',
                'verbose_name': '\u0421\u0435\u0430\u043d\u0441 \u0432 Rambler.Kassa',
                'verbose_name_plural': '\u0421\u0435\u0430\u043d\u0441\u044b \u0432 Rambler.Kassa',
            },
        ),
        migrations.AlterModelOptions(
            name='kassybuilding',
            options={'verbose_name': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0432 kassy.ru', 'verbose_name_plural': '\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0432 kassy.ru'},
        ),
        migrations.AlterModelOptions(
            name='kassysession',
            options={'get_latest_by': 'datetime', 'verbose_name': '\u0441\u0435\u0430\u043d\u0441 \u0432 kassy.ru', 'verbose_name_plural': '\u0441\u0435\u0430\u043d\u0441\u044b \u0432 kassy.ru'},
        ),
        migrations.RenameField(
            model_name='kassyhall',
            old_name='kassy_building_id',
            new_name='building',
        ),
        migrations.AlterField(
            model_name='kassyhall',
            name='building',
            field=models.ForeignKey(related_name='halls', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='afisha.KassyBuilding', null=True),
        ),
        migrations.RenameField(
            model_name='kassysession',
            old_name='date',
            new_name='datetime',
        ),
        migrations.RenameField(
            model_name='kassysession',
            old_name='kassy_event',
            new_name='event',
        ),
        migrations.AlterField(
            model_name='kassysession',
            name='event',
            field=models.ForeignKey(related_name='sessions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435', to='afisha.KassyEvent', null=True),
        ),
        migrations.RenameField(
            model_name='kassysession',
            old_name='kassy_hall',
            new_name='hall',
        ),
        migrations.AlterField(
            model_name='kassysession',
            name='hall',
            field=models.ForeignKey(related_name='sessions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u0437\u0430\u043b', to='afisha.KassyHall', null=True),
        ),
        migrations.AlterField(
            model_name='kassybuilding',
            name='guide',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Guide', verbose_name='\u0437\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435 \u0433\u0438\u0434\u0430'),
        ),
        migrations.AlterField(
            model_name='kassybuilding',
            name='id',
            field=models.IntegerField(serialize=False, verbose_name='ID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='kassyevent',
            name='id',
            field=models.IntegerField(serialize=False, verbose_name='ID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='kassyhall',
            name='hall',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Hall', verbose_name='\u0437\u0430\u043b'),
        ),
        migrations.AlterField(
            model_name='kassyrollerman',
            name='id',
            field=models.IntegerField(serialize=False, verbose_name='ID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='kassysession',
            name='current_session',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.CurrentSession', verbose_name='\u0441\u0435\u0430\u043d\u0441'),
        ),
        migrations.AlterField(
            model_name='kassysession',
            name='id',
            field=models.IntegerField(serialize=False, verbose_name='ID', primary_key=True),
        ),
        migrations.AddField(
            model_name='ramblerevent',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Event', verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='kassyevent',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Event', verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435'),
        ),
        migrations.AddField(
            model_name='kinomaxevent',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='afisha.Event', verbose_name='\u0441\u043e\u0431\u044b\u0442\u0438\u0435'),
        ),
        migrations.AlterUniqueTogether(
            name='ramblerhall',
            unique_together=set([('hallid', 'building')]),
        ),
    ]
