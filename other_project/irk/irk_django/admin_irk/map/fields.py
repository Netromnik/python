# -*- coding: utf-8 -*-

import types

from django import forms
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import Point


class PointWidget(forms.widgets.HiddenInput):

    def __init__(self, width=800, height=500, field=None, type=None, zoom=12, *args, **kwargs):
        self.width = width
        self.height = height
        self.type = type
        self.zoom = zoom
        self.field = field
        super(PointWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, *args, **kwargs):
        if value:
            if isinstance(value, types.StringTypes):
                lat, lng = value.split(',')
            else:
                lat, lng = value

                lat, lng = float(lat), float(lng)
        else:
            lat, lng = None, None

        scheme = 'https' if settings.FORCE_HTTPS else 'http'

        template = get_template('map/snippets/PointWidgetYandex.html')
        js = template.render(Context({'field': self.field, 'name': name, 'lat': lat, 'lng': lng,
                                      'type': self.type, 'zoom': self.zoom, 'scheme': scheme}))
        html = super(PointWidget, self).render(name, "%s,%s" % (lat, lng) if lat and lng else None, {'id': 'id_%s' % name})
        html += '<div id="map_%s" class="gmap" style="width: %dpx; height: %dpx"></div>' % (name, self.width, self.height)

        return mark_safe(js+html)


class PointField(forms.Field):
    widget = PointWidget

    def to_python(self, value):
        if value:
            if isinstance(value, unicode):
                lat, lng = value.strip().split(',')
            else:
                lat, lng = value

            lat, lng = float(lat), float(lng)
            return Point(lat, lng)


class PointTextWidget(forms.widgets.TextInput):

    def value_from_object(self, data):
        return data

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, Point):
            value = '%0.16f,%0.16f' % (value.x, value.y)
        return super(PointTextWidget, self).render(name, value, attrs)


class InlinePointField(PointField):
    widget = PointTextWidget
