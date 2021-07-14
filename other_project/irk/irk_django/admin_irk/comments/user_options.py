# -*- coding: utf-8 -*-

from irk.profiles.options import Option


class CommentsSortOption(Option):
    """
    Сортировка комментариев
    """

    choices = ('asc', 'desc', 'top')
    cookie_key = 'cs'
    default = 'asc'
    multiple = False

    def load_value_from_cookie(self, value):
        return str(value)

    def prepare_value_for_cookie(self, value):
        return str(value)

    def load_value_from_db(self, value):
        return str(value)

    def prepare_value_for_db(self, value):
        return str(value)
