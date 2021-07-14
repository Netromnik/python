# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import irk.gallery.models
import irk.utils.fields.file
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, editable=False)),
                ('stamp', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('content_type', models.ForeignKey(blank=True, editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': '\u0433\u0430\u043b\u0435\u0440\u0435\u044e',
                'verbose_name_plural': '\u0433\u0430\u043b\u0435\u0440\u0435\u0438',
            },
        ),
        migrations.CreateModel(
            name='GalleryPicture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveSmallIntegerField(verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f', blank=True)),
                ('main', models.BooleanField(default=False, verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f')),
                ('best', models.BooleanField(default=False, verbose_name='\u041b\u0443\u0447\u0448\u0430\u044f')),
                ('gallery', models.ForeignKey(verbose_name='\u0413\u0430\u043b\u0435\u0440\u0435\u044f', to='gallery.Gallery')),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': '\u0440\u0438\u0441',
                'verbose_name_plural': '\u0440\u0438\u0441.',
            },
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.gallery.models.upload_to, verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435')),
                ('title', models.CharField(max_length=255, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('watermark', models.BooleanField(default=False, verbose_name='\u0412\u043e\u0442\u0435\u0440\u043c\u0430\u0440\u043a')),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435',
            },
        ),
        migrations.AddField(
            model_name='gallerypicture',
            name='picture',
            field=models.ForeignKey(verbose_name='\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435', to='gallery.Picture'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='pictures',
            field=models.ManyToManyField(to='gallery.Picture', through='gallery.GalleryPicture'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='gallerypicture',
            unique_together=set([('picture', 'gallery')]),
        ),
    ]
