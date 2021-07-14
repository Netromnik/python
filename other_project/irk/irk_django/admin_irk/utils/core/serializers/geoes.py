# -*- coding: utf-8 -*-

"""Сериализатор гео-полей в формате elasticsearch"""

import json
import StringIO

from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers.json import Serializer as OverloadedSerializer
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.geos import Point
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.core.serializers.python import Deserializer as PythonDeserializer


class Serializer(OverloadedSerializer):
    def handle_field(self, obj, field):
        """
        If field is of GeometryField than encode otherwise call parent's method
        """
        value = field._get_val_from_obj(obj)
        if isinstance(field, GeometryField):
            self._current[field.name] = value
        else:
            super(Serializer, self).handle_field(obj, field)


    def end_serialization(self):
        json.dump(self.objects, self.stream, cls=ElasticSearchGEOJSONEncoder, **self.options)


class ElasticSearchGEOJSONEncoder(DjangoJSONEncoder):
    """
    DjangoGEOJSONEncoder subclass that knows how to encode GEOSGeometry value
    """

    def default(self, o):
        """ overload the default method to process any GEOSGeometry objects otherwise call original method """

        if isinstance(o, Point):
            return [o.x, o.y]
        elif isinstance(o, GEOSGeometry):
            return json.loads(o.geojson)

        return super(ElasticSearchGEOJSONEncoder, self).default(o)


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    def GEOJsonToEWKT(dict):
        """
        Convert to a string that GEOSGeometry class constructor can accept.

        The default decoder would pass our geo dict object to the constructor which
        would result in a TypeError; using the below hook we are forcing it into a
        ewkt format. This is accomplished with a class hint as per JSON-RPC
        """
        if '__GEOSGeometry__' in dict:  # using class hint catch a GEOSGeometry definition
            return dict['__GEOSGeometry__'][1][0]

        return dict
    if isinstance(stream_or_string, basestring):
        stream = StringIO.StringIO(stream_or_string)
    else:
        stream = stream_or_string
    for obj in PythonDeserializer(json.load(stream, object_hook=GEOJsonToEWKT), **options):
        yield obj
