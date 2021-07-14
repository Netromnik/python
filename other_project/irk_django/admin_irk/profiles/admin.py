# -*- coding: utf-8 -*-

import time
import operator
import datetime
from functools import update_wrapper

from django.db import models
from django.db.models import Q
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib import messages
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, render, render
from django.http import HttpResponseRedirect
from django.contrib.admin.utils import lookup_needs_distinct
from social_django.models import UserSocialAuth

from irk.profiles.models import BounceEvent, Profile, UserBanHistory, ProfileBannedUser, ProfileSocial
from irk.profiles.forms import UserAdminForm, ProfileBanForm, ProfileAdminInlineForm, UserAddAdminForm
from irk.profiles.forms.admin import CorporativeProfileAdminForm, ChangePasswordProfileAdminForm
from irk.utils.notifications import tpl_notify
from irk.utils.files.admin import admin_media_static


admin.site.unregister(User)
admin.site.unregister(Group)


class ProfileUser(User):
    """Прокси-модель для редактирования моделей User и Profile на одной странице"""

    class Meta:
        proxy = True
        verbose_name = u'пользователь'
        verbose_name_plural = u'пользователи'


class ProfileGroup(Group):
    class Meta:
        proxy = True
        verbose_name = u'группe'
        verbose_name_plural = u'группы'


admin.site.register(ProfileGroup, GroupAdmin)


class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileAdminInlineForm
    extra = 1
    max_num = 1


class UserSocialAuthInline(admin.StackedInline):
    model = UserSocialAuth
    extra = 0

class UserChangePasswordMixin(object):
    """
    Примесь для смены пароля пользователя

        NOTE: Так как ProfileChangelist возвращает объекты модели User, а не Profile и по причине того, что модели
        Profile и User не взаимозаменяемы (они связаны не через pk, а через user_id), пришлось перегрузить этот миксин
        для CorporativeUserAdmin.
    """

    password_form = ChangePasswordProfileAdminForm

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.object_name.lower()

        return [url(r'^(.+)/change/password/$', wrap(self.changepassword_view),
                    name='{}_{}_changepassword'.format(*info)),
                ] + super(UserChangePasswordMixin, self).get_urls()

    def changepassword_view(self, request, object_id):
        profile = self.get_profile(object_id)
        user = profile.user

        if request.POST:
            form = self.password_form(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.save()

                messages.success(request, u'Пароль успешно изменен')

                return HttpResponseRedirect('..')
        else:
            form = self.password_form()

        context = {
            'object': profile,
            'form': form,
            'opts': self.model._meta,
            'has_change_permission': True,
            'title': u'Смена пароля',
        }

        return render(request, 'admin/profiles/profile/password.html', context)

    def get_profile(self, object_id):
        """Получить профиль для редактирования"""

        profile = get_object_or_404(Profile, user_id=object_id)

        return profile


class ProfileChangePasswordMixin(UserChangePasswordMixin):
    """Примесь для смены пароля через профиль пользователя"""

    def get_profile(self, object_id):
        """Получить профиль для редактирования"""

        profile = get_object_or_404(Profile, id=object_id)

        return profile


class ProfileChangelist(ChangeList):
    """
    ChangeList перегружен для того, чтобы иметь возможность искать как по полям `django.contrib.auth.models.User`,
    так и по полям `profiles.models.Profile`.
    """

    def get_queryset(self, request):
        search_query = self.query
        self.query = None

        qs = super(ProfileChangelist, self).get_queryset(request)

        self.query = search_query

        # First, we collect all the declared list filters.
        (self.filter_specs, self.has_filters, remaining_lookup_params,
         use_distinct) = self.get_filters(request)

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        if self.search_fields and self.query:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in self.search_fields]
            for bit in self.query.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                qs = qs.filter(reduce(operator.or_, or_queries))
            if not use_distinct:
                for search_spec in orm_lookups:
                    if lookup_needs_distinct(self.lookup_opts, search_spec):
                        use_distinct = True
                        break

            # profiles = Profile.objects.filter(user_id__in=qs, full_name__icontains=self.query).values_list('user_id', flat=True).distinct()
            profiles = Profile.objects.filter(Q(user_id__in=qs) | Q(full_name__icontains=self.query)) \
                .values_list('user_id', flat=True).distinct()
            qs = User.objects.filter(id__in=profiles)

        if use_distinct:
            return qs.distinct()
        else:
            return qs


@admin.register(ProfileUser)
class ProfileUserAdmin(UserChangePasswordMixin, UserAdmin):
    form = UserAdminForm
    add_form = UserAddAdminForm
    inlines = (ProfileInline, UserSocialAuthInline)
    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    list_display = ('__unicode__', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    def has_add_permission(self, request):
        opts = self.opts

        return request.user.has_perm(opts.app_label + '.add_profile')

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.change_profile')

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.delete_profile')

    def get_changelist(self, request, **kwargs):
        return ProfileChangelist

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'user_permissions':
            # Небольшая оптимизация при выводе прав пользователя
            kwargs['queryset'] = Permission.objects.all().select_related()

        return super(ProfileUserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class CorporativeProfile(Profile):

    class Meta:
        proxy = True
        verbose_name = u'корпоративный аккаунт'
        verbose_name_plural = u'корпоративные аккаунты'


class ProfileSocialInline(admin.TabularInline):
    model = ProfileSocial
    extra = 1


class CorporativeUserAdmin(ProfileChangePasswordMixin, admin.ModelAdmin):
    """Админка для корпоративных пользователей"""

    inlines = (ProfileSocialInline, )
    ordering = ('-id', )
    list_display = ('full_name', 'company_name')
    search_fields = ('full_name', 'company_name')
    fieldsets = (
        (None, {
            'fields': ('full_name', 'company_name', 'email', 'type', 'image', 'phone'),
        }),
    )
    form = CorporativeProfileAdminForm

    def get_queryset(self, request):
        return super(CorporativeUserAdmin, self).get_queryset(request).filter(type=Profile.TYPE_CORPORATIVE)

    def save_model(self, request, obj, form, change):
        if not change:
            user = self._create_user()
            obj.is_verified = True
        else:
            user = obj.user

        user.email = form.cleaned_data['email']
        user.save()

        obj.user = user
        obj.save()

    def _create_user(self):
        user = User()
        while True:
            username = 'irk-{0}'.format(time.time())
            if not User.objects.filter(username=username).exists():
                user.username = username
                break
        user.set_unusable_password()

        return user


admin.site.register(CorporativeProfile, CorporativeUserAdmin)


class ProfileBannedUserAdmin(admin.ModelAdmin):
    """Список забаненных пользователей"""

    form = ProfileBanForm
    ordering = ('-bann_end',)
    list_display = ('user', 'bann_end', 'ban_info', 'history_link')
    list_select_related = True
    search_fields = ('user__username', 'full_name')
    change_form_template = 'admin/profiles/ban/change_form.html'

    @admin_media_static
    class Media(object):
        css = {
            'all': ('tourism/css/admin.css', 'profiles/css/admin.css'),
        }
        js = ('js/apps-js/admin.js', 'tourism/js/admin.js')

    def has_add_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.can_ban_profile')

    has_change_permission = has_delete_permission = has_add_permission

    def get_queryset(self, request):
        return super(ProfileBannedUserAdmin, self).get_queryset(request).filter(is_banned=True)

    def save_form(self, request, form, change):
        user = form.cleaned_data['user']
        profile = Profile.objects.get(user=user)

        period = form.cleaned_data['period']  # Используется в шаблоне
        if period > 0:
            ended = datetime.datetime.now() + datetime.timedelta(period)
        else:
            # Пожизненный бан - NULL в базе
            ended = None

        profile.is_banned = True
        profile.bann_end = ended
        profile.save()

        if change:
            # Отредактирован старый бан
            try:
                history = UserBanHistory.objects.filter(user=user).order_by('-created')[0]
            except IndexError:
                history = UserBanHistory(user=user, created=datetime.datetime.now())
                # обновляем запись в истории
            history.moderator = request.user
            history.ended = ended
            history.reason = form.cleaned_data['reason']
            history.save()
        else:
            # Пользователь снова оказался в бане
            history = UserBanHistory(moderator=request.user, user=user, reason=form.cleaned_data['reason'],
                                     created=datetime.datetime.now(), ended=ended)
            history.save()

            tpl_notify(u'Ваш аккаунт на Ирк.ру заблокирован', "notif/ban.html", {'period': period, 'user': user},
                       request, [user.email, ])

        return profile

    def delete_model(self, request, obj):
        obj.is_banned = False
        obj.save()
        user = obj.user
        tpl_notify(u'Ваш аккаунт на Ирк.ру разблокирован', "notif/unban.html", {'user': user}, request,
                   [obj.user.email, ])

    def history_view(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(ProfileBannedUser, pk=user_id).user
        objects = UserBanHistory.objects.filter(user=user).select_related().order_by('-created')

        return render(request, 'admin/profiles/ban/history.html', {'object': user, 'objects': objects})

    def ban_info(self, obj):
        try:
            info = UserBanHistory.objects.filter(user=obj.user).order_by('-created')[0]
            return u'%s: %s' % (info.moderator, info.reason)
        except IndexError:
            return u''

    ban_info.short_description = u'Дополнительная информация'

    def history_link(self, obj):
        return u'<a href="./%s/history/">История</a>' % obj.pk

    history_link.allow_tags = True
    history_link.short_description = u'История банов'

    def response_change(self, request, obj):
        obj._meta.model_name = 'profilebanneduser'

        return super(ProfileBannedUserAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        return HttpResponseRedirect('..')


admin.site.register(ProfileBannedUser, ProfileBannedUserAdmin)


class BounceEventAdmin(admin.ModelAdmin):
    list_display = ('email', 'message_date', 'created_at')
    readonly_fields = ('email', 'message_date', 'date', 'message_id', 'hash', 'details', 'created_at', 'user')
    fields = readonly_fields
    search_fields = ('email', )


admin.site.register(BounceEvent, BounceEventAdmin)
