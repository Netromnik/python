# -*- coding: utf-8 -*-

from django.db import models


class SitesManager(models.Manager):

    def get_by_path(self, name):
        path = '/'
        data = None
        for _path in name.strip('/').split('/'):
            path = '%s%s/' % (path, _path)
            _data = self.filter(url__iendswith=path)
            if not _data.count():
                break
            else:
                data = _data[0]

        return data.site

    def get_by_domain(self, domain):
        try:
            return self.get(slugs__icontains=domain)
        except self.model.DoesNotExist:
            return None

    def get_by_alias(self, alias):
        try:
            return self.get_queryset().filter(slugs=alias)[0]
        except IndexError:
            raise self.model.DoesNotExist()

    def get_by_pk(self, pk):
        if not pk:
            return
        try:
            return self.get_queryset().filter(pk=pk)[0]
        except IndexError:
            raise self.model.DoesNotExist('Site with a PK %s does not exists' % pk)
