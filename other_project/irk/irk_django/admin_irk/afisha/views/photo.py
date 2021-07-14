# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.core.urlresolvers import reverse

from irk.afisha.models import Photo
from irk.news.views.photo import PhotoReadView as NewsPhotoReadView


class PhotoReadView(NewsPhotoReadView):
    model = Photo
    template = 'afisha/photo/read.html'

read = PhotoReadView.as_view()
