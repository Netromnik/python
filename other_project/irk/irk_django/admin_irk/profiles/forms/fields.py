# -*- coding: utf-8 -*-

import re

from django_select2.fields import AutoModelSelect2Field, AutoHeavySelect2Widget

from irk.profiles.models import Profile


SKIPPED_USERNAME_RE = re.compile('^irk-\d+')


class UserAutocompleteWidget(AutoHeavySelect2Widget):
    def label_from_instance(self, obj):
        full_name = obj.full_name
        username = obj.user.username
        if SKIPPED_USERNAME_RE.match(username):
            username = None

        if full_name and username:
            return u'{} ({})'.format(full_name, username)
        if full_name and not username:
            return full_name
        return username

    def render_texts_for_value(self, id_, value, choices):
        """Переопределяем метод, потому что в `django_select2.widgets.HeavySelect2Mixin.render_texts`
        делается выборка Profile.objects.select_related('user'), которая нигде не используется,
        но занимает много времени"""

        try:
            profile = Profile.objects.get(id=value)
            return u"$('#{}').txt('{}');".format(id_, self.label_from_instance(profile))
        except (ValueError, Profile.DoesNotExist):
            return


class UserAutocompleteField(AutoModelSelect2Field):
    queryset = Profile.objects.select_related('user')
    search_fields = ('full_name__icontains', 'user__username__icontains', 'user__first_name__icontains',
                     'user__last_name__icontains', 'phone__icontains', 'user__email__icontains')
    to_field_name = 'user_id'
    widget = UserAutocompleteWidget

    def label_from_instance(self, obj):
        return self.widget.label_from_instance(obj)

    def to_python(self, value):
        try:
            return Profile.objects.get(id=value).user
        except (TypeError, ValueError, Profile.DoesNotExist):
            return None

    def prepare_value(self, value):
        value = super(UserAutocompleteField, self).prepare_value(value)

        try:
            if not value:
                raise Profile.DoesNotExist()
            return self.queryset.get(user_id=value).pk
        except Profile.DoesNotExist:
            return value
