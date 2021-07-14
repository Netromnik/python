# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import tempfile
import filecmp

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django_dynamic_fixture import G
from sorl.thumbnail.main import Thumbnail
from sorl.thumbnail.processors import dynamic_import
from irk.tests.unit_base import UnitTestBase
from irk.gallery.models import Picture


settings.WATERMARK = 'img/tests/watermark.png'
settings.THUMBNAIL_EXTENSION = 'png'


class WatermarkTest(UnitTestBase):

    def test_set_watermark(self):

        image_source = 'img/tests/test_source.png'
        image_result = 'img/tests/test_result.png'
        destination = '/tmp/irkru_watermark_test.png'

        image = G(Picture, image=image_source, watermark=True)
        tmp_file = tempfile.NamedTemporaryFile(delete=False)

        thumbnail = Thumbnail(find(image_source), (500, 500), quality=100, opts={
            'x': image.watermark,
        }, processors=dynamic_import(settings.THUMBNAIL_PROCESSORS), dest=destination)
        thumbnail.generate()

        self.assertTrue(filecmp.cmp(find(image_result), thumbnail.dest),
                        "Can't compare %s and %s" % (image_result, thumbnail.dest))
        os.remove(destination)
