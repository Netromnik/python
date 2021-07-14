# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals


class Formatter(object):
    """
    Processor formatter base class
    """

    def __call__(self, name, value, options, parent, context):
        self.name = name
        self.value = value
        self.options = options
        self.parent = parent
        self.context = context

        return self.render()

    def render(self):
        raise NotImplementedError('Implement it in subclasses')
