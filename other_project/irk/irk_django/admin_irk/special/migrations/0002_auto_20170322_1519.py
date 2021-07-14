# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('special', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('link', models.URLField(verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True)),
                ('image', models.ImageField(upload_to=b'img/site/special/project/sponsor/', verbose_name='\u041b\u043e\u0433\u043e\u0442\u0438\u043f')),
            ],
            options={
                'verbose_name': '\u0421\u043f\u043e\u043d\u0441\u043e\u0440',
                'verbose_name_plural': '\u0421\u043f\u043e\u043d\u0441\u043e\u0440\u044b',
            },
        ),
        migrations.AddField(
            model_name='sponsor',
            name='project',
            field=models.ForeignKey(verbose_name='\u0421\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442', to='special.Project'),
        ),
        migrations.AddField(
            model_name='project',
            name='banner_right',
            field=models.ForeignKey(related_name='project_banner_right',
                                    verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0431\u0430\u043d\u043d\u0435\u0440\u0430 \u0432 \u043f\u0440\u0430\u0432\u043e\u0439 \u043a\u043e\u043b\u043e\u043d\u043a\u0435 \u0441\u0442\u0430\u0442\u0435\u0439',
                                    to='adv.Place', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='branding_bottom',
            field=models.ForeignKey(related_name='project_branding_bottom',
                                    verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0431\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u0432\u043d\u0438\u0437\u0443 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b',
                                    to='adv.Place', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='branding_top',
            field=models.ForeignKey(related_name='project_branding_top',
                                    verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f \u0431\u0440\u0435\u043d\u0434\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u0432\u0432\u0435\u0440\u0445\u0443 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b',
                                    to='adv.Place', null=True, blank=True),
        ),
    ]
