# -*- coding: utf-8 -*-

from irk.utils.search import ModelSearch


class ExpertSearch(ModelSearch):
    fields = ('title', 'content', 'caption', 'specialist')
    boost = {
        'title': 1.0,
        'caption': 0.5,
        'content': 0.4,
        'specialist': 0.2,
    }
