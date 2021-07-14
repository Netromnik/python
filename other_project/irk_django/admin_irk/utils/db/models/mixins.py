# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.core.serializers import serialize


class SerializerMixin(object):
    """
    Serialized representation for models
    """

    serialized_fields = None

    def as_json(self, fields=None):
        """JSON serialization"""

        fields = fields or self.serialized_fields
        data = serialize('json', [self], fields=fields)

        return data
