# -*- coding: UTF-8 -*-
from irk.profiles.options import Option


class SessionType(Option):
    cookie_key = 'st'
    template = 'afisha/snippets/sessions_switcher.html'

    def get_choices(self):
        return (1, 'еще не начавшиеся'), (2, 'все на сегодня')

    choices = property(get_choices)

    def get_default(self):
        return 1

    default = property(get_default)

    def load_value_from_cookie(self, value):
        return int(value)

    def set_value(self, value):
        return super(SessionType, self).set_value(int(value))

    class Meta:
        verbose_name = u'События'
