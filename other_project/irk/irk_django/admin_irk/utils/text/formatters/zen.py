# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from irk.utils.text.formatters.bb import ImageFormatter as DefaultImageFormatter


class ImageFormatter(DefaultImageFormatter):
    template = 'bb_codes/zen/image.html'
