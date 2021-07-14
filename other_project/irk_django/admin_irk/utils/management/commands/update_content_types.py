# -*- coding: utf-8 -*-

from django.apps import apps as django_apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.management import update_contenttypes
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from irk.news.models import BaseMaterial


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            default=False,
                            help=u'Удаляем content types, к которым больше нет соответствующих моделей')

    plural_names = {
        'news': u'Новости раздела',
        'article': u'Статьи раздела',
        'sitenews': u'Новости раздела',
        'sitearticle': u'Статьи раздела',
        'sitephoto': u'Фоторепортажи раздела',
        'sitevideo': u'Видео раздела',
        'sitepoll': u'Голосование раздела',
    }

    def handle(self, *args, **options):

        for app in django_apps.get_app_configs():
            update_contenttypes(app, None, 2, db='default')

        apps = set()
        for model in django_apps.get_models():
            if not issubclass(model, BaseMaterial):
                continue

            apps.add(model._meta.app_label)

        for app in apps:
            for model_name in ('news', 'article', 'sitenews', 'sitearticle', 'sitephoto', 'sitevideo', 'sitepoll'):
                try:
                    ct = ContentType.objects.get(app_label=app, model=model_name)
                except ContentType.DoesNotExist:
                    continue

                for perm_name in ('can_change',):
                    try:
                        perm = Permission.objects.get(content_type=ct, codename__icontains=perm_name)
                    except Permission.DoesNotExist:
                        perm = Permission.objects.create(content_type=ct, codename=perm_name, name=self.plural_names[model_name])
                    else:
                        perm.codename = perm_name
                        perm.save()

        if options['delete']:
            for ct in ContentType.objects.all():
                print 'Deleting %s.%s' % (ct.app_label, ct.name)
                if not ct.model_class():
                    ct.delete()
