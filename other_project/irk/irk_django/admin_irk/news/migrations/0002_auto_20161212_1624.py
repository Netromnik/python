# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import irk.news.models
import irk.utils.managers
import irk.utils.fields.file
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0001_initial'),
        ('polls', '0001_initial'),
        ('options', '0001_initial'),
        ('special', '0001_initial'),
        ('testing', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
            ],
            options={
                'verbose_name': '\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u0435',
                'proxy': True,
                'verbose_name_plural': '\u0433\u043e\u043b\u043e\u0441\u043e\u0432\u0430\u043d\u0438\u044f \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('polls.poll',),
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
            ],
            options={
                'verbose_name': '\u0442\u0435\u0441\u0442',
                'proxy': True,
                'verbose_name_plural': '\u0442\u0435\u0441\u0442\u044b \u0440\u0430\u0437\u0434\u0435\u043b\u0430',
            },
            bases=('testing.test',),
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('bigfoot_image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 1920\u0445600 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u0447\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f \u0434\u043b\u044f \u0431\u0438\u0433\u0444\u0443\u0442\u0430', blank=True)),
                ('image_label', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u044c \u0434\u043b\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438', blank=True)),
                ('is_paid', models.BooleanField(default=False, db_index=True, verbose_name='\u041f\u043b\u0430\u0442\u043d\u0430\u044f')),
                ('was_paid', models.BooleanField(default=False, help_text='\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0434\u043b\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0438', db_index=True, verbose_name='\u041f\u043b\u0430\u0442\u043d\u044b\u0439 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b')),
                ('paid', models.DateTimeField(db_index=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438 \u043f\u043b\u0430\u0442\u043d\u043e\u0439', null=True, editable=False, blank=True)),
                ('introduction', models.CharField(max_length=1000, verbose_name='\u0412\u0432\u0435\u0434\u0435\u043d\u0438\u0435', blank=True)),
                ('is_bigfoot', models.BooleanField(default=False, db_index=True, verbose_name='\u0421\u0442\u0430\u0442\u044c\u044f \u0431\u0438\u0433\u0444\u0443\u0442')),
                ('type', models.ForeignKey(related_name='articles', verbose_name='\u0422\u0438\u043f', to='news.ArticleType')),
            ],
            options={
                'db_table': 'news_article',
                'verbose_name': '\u0441\u0442\u0430\u0442\u044c\u044f',
                'verbose_name_plural': '\u0441\u0442\u0430\u0442\u044c\u0438',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='DailyNewsletter',
            fields=[
                ('basenewsletter_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseNewsletter')),
                ('date', models.DateField(verbose_name='\u0434\u0430\u0442\u0430 \u043e\u0442\u043f\u0440\u0430\u0432\u043a\u0438', db_index=True)),
            ],
            bases=('news.basenewsletter',),
        ),
        migrations.CreateModel(
            name='Infographic',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('image', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 960\xd7&infin; \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/news/infographic', verbose_name='\u0418\u043d\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430')),
                ('preview', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940x445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/news/infographic', verbose_name='\u041f\u0440\u0435\u0432\u044c\u044e')),
                ('thumbnail', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 300\xd7200 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/news/infographic', verbose_name='\u041c\u0438\u043d\u0438\u0430\u0442\u044e\u0440\u0430')),
                ('iframe_url', models.CharField(max_length=100, verbose_name='\u0410\u0434\u0440\u0435\u0441 iframe', blank=True)),
                ('iframe_height', models.PositiveIntegerField(default=600)),
            ],
            options={
                'db_table': 'news_infographics',
                'verbose_name': '\u0438\u043d\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430',
                'verbose_name_plural': '\u0438\u043d\u0444\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='Metamaterial',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('url', models.URLField(verbose_name='\u0441\u0441\u044b\u043b\u043a\u0430')),
                ('image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('image_3x2', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 705\u0445470. \u041f\u0440\u043e\u043f\u043e\u0440\u0446\u0438\u044f 3:2', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0421\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('is_special', models.BooleanField(default=False, db_index=True, verbose_name='\u0421\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442')),
                ('show_on_home', models.BooleanField(default=False, db_index=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0432 \u0431\u043b\u043e\u043a\u0435 \u0421\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432 \u043d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u0439')),
            ],
            options={
                'verbose_name': '\u043c\u0435\u0442\u0430\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b',
                'verbose_name_plural': '\u043c\u0435\u0442\u0430\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u044b',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('caption_short', models.TextField(verbose_name='\u041f\u043e\u0434\u0432\u043e\u0434\u043a\u0430 \u0434\u043b\u044f SMS', blank=True)),
                ('is_main', models.BooleanField(default=False, db_index=True, verbose_name='\u0413\u043b\u0430\u0432\u043d\u0430\u044f')),
                ('is_payed', models.BooleanField(default=False, db_index=True, verbose_name='\u041f\u043b\u0430\u0442\u043d\u0430\u044f')),
                ('is_exported', models.BooleanField(default=True, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f \u0432 \u042f\u043d\u0434\u0435\u043a\u0441.\u043d\u043e\u0432\u043e\u0441\u0442\u044f\u0445')),
                ('has_video', models.BooleanField(default=False, db_index=True, verbose_name='\u0415\u0441\u0442\u044c \u0432\u0438\u0434\u0435\u043e')),
                ('image', irk.utils.fields.file.ImageRemovableField(upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0411\u043e\u043b\u044c\u0448\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('bunch', models.ForeignKey(related_name='news_bunch', default=None, blank=True, to='news.News', null=True, verbose_name='\u041f\u0440\u0435\u0434\u044b\u0434\u0443\u0449\u0430\u044f \u0441\u0432\u044f\u0437\u0430\u043d\u043d\u0430\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u044c')),
                ('city', models.ForeignKey(verbose_name='\u0413\u043e\u0440\u043e\u0434', blank=True, to='map.Cities', null=True)),
            ],
            options={
                'db_table': 'news_news',
                'verbose_name': '\u043d\u043e\u0432\u043e\u0441\u0442\u044c',
                'verbose_name_plural': '\u043d\u043e\u0432\u043e\u0441\u0442\u0438',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('caption_short', models.TextField(help_text='\u041d\u0435 \u0431\u043e\u043b\u044c\u0448\u0435 290 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432', max_length=290, verbose_name='\u0421\u043e\u043a\u0440\u0430\u0449\u0435\u043d\u043d\u0430\u044f \u043f\u043e\u0434\u0432\u043e\u0434\u043a\u0430 (\u0434\u043b\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u0438)', blank=True)),
                ('image', models.ImageField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 940\u0445445 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=irk.news.models.wide_image_upload_to, verbose_name='\u0428\u0438\u0440\u043e\u043a\u043e\u0444\u043e\u0440\u043c\u0430\u0442\u043d\u0430\u044f \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044f', blank=True)),
                ('was_paid', models.BooleanField(default=False, help_text='\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0434\u043b\u044f \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0438', db_index=True, verbose_name='\u041f\u043b\u0430\u0442\u043d\u044b\u0439 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b')),
                ('share_text', models.CharField(max_length=255, verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u044c \u0434\u043b\u044f \u0441\u043e\u0446\u0438\u043e\u043a\u043d\u043e\u043f\u043e\u043a', blank=True)),
            ],
            options={
                'db_table': 'news_photo',
                'verbose_name': '\u0444\u043e\u0442\u043e\u0440\u0435\u043f\u043e\u0440\u0442\u0430\u0436',
                'verbose_name_plural': '\u0444\u043e\u0442\u043e\u0440\u0435\u043f\u043e\u0440\u0442\u0430\u0436\u0438',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('basematerial_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseMaterial')),
                ('preview', irk.utils.fields.file.ImageRemovableField(help_text='\u0420\u0430\u0437\u043c\u0435\u0440: 800x378 \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439', upload_to=b'img/site/news/video', verbose_name='\u041f\u0440\u0435\u0432\u044c\u044e')),
            ],
            options={
                'db_table': 'news_video',
                'verbose_name': '\u0432\u0438\u0434\u0435\u043e',
                'verbose_name_plural': '\u0432\u0438\u0434\u0435\u043e',
            },
            bases=('news.basematerial',),
        ),
        migrations.CreateModel(
            name='WeeklyNewsletter',
            fields=[
                ('basenewsletter_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='news.BaseNewsletter')),
                ('year', models.PositiveSmallIntegerField(verbose_name='\u0433\u043e\u0434')),
                ('week', models.PositiveSmallIntegerField(verbose_name='\u043d\u0435\u0434\u0435\u043b\u044f')),
            ],
            bases=('news.basenewsletter',),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='quote',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='position',
            name='block',
            field=models.ForeignKey(related_name='positions', to='news.Block'),
        ),
        migrations.AddField(
            model_name='position',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='materialnewsletterrelation',
            name='material',
            field=models.ForeignKey(related_name='+', to='news.BaseMaterial'),
        ),
        migrations.AddField(
            model_name='materialnewsletterrelation',
            name='newsletter',
            field=models.ForeignKey(related_name='material_relations', to='news.BaseNewsletter'),
        ),
        migrations.AddField(
            model_name='liveentry',
            name='live',
            field=models.ForeignKey(related_name='entries', to='news.Live'),
        ),
        migrations.AddField(
            model_name='flash',
            name='author',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='basenewsletter',
            name='materials',
            field=models.ManyToManyField(related_name='_basenewsletter_materials_+', through='news.MaterialNewsletterRelation', to='news.BaseMaterial'),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='category',
            field=models.ForeignKey(related_name='news_basematerial', verbose_name='\u0420\u0443\u0431\u0440\u0438\u043a\u0430', blank=True, to='news.Category', null=True),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='content_type',
            field=models.ForeignKey(blank=True, editable=False, to='contenttypes.ContentType', null=True, verbose_name='\u0442\u0438\u043f \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0430'),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='persons',
            field=models.ManyToManyField(related_name='news_basematerial', verbose_name='\u041f\u0435\u0440\u0441\u043e\u043d\u044b', to='news.Person', blank=True),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='project',
            field=models.ForeignKey(related_name='news_materials', default=None, blank=True, to='special.Project', null=True, verbose_name='\u0421\u043f\u0435\u0446\u043f\u0440\u043e\u0435\u043a\u0442'),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='sites',
            field=models.ManyToManyField(related_name='news_basematerial', verbose_name='\u0420\u0430\u0437\u0434\u0435\u043b\u044b', to='options.Site'),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='source_site',
            field=models.ForeignKey(verbose_name='\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0440\u0430\u0437\u0434\u0435\u043b', blank=True, to='options.Site', null=True),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='subject',
            field=models.ForeignKey(related_name='news_basematerial', verbose_name='\u0421\u044e\u0436\u0435\u0442', blank=True, to='news.Subject', null=True),
        ),
        migrations.AddField(
            model_name='basematerial',
            name='tags',
            field=irk.utils.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AlterUniqueTogether(
            name='materialnewsletterrelation',
            unique_together=set([('material', 'newsletter')]),
        ),
        migrations.AddField(
            model_name='live',
            name='news',
            field=models.ForeignKey(to='news.News'),
        ),
        migrations.AlterIndexTogether(
            name='basematerial',
            index_together=set([('stamp', 'published_time')]),
        ),
    ]
