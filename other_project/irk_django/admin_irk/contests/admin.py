# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.safestring import mark_safe

from irk.contests.forms import ContestAdminForm
from irk.contests.models import Contest, Participant
from irk.gallery.admin import GalleryInline
from irk.news.admin import BaseMaterialAdmin
from irk.ratings.models import Rate
from irk.utils.decorators import options
from irk.utils.files.admin import admin_media_static
from irk.utils.notifications import tpl_notify


class ParticipantInline(admin.StackedInline):
    """
    Блок списка участников на странице конкурса
    """
    model = Participant
    fields = ('_get_votes', )
    readonly_fields = ('_get_votes', )

    @options(short_description=u'Голоса', allow_tags=False)
    def _get_votes(self, participant):
        """
        Сколько людей проголосовало за этого участника
        """
        return participant.rating_object.total_sum


@admin.register(Contest)
class ContestAdmin(BaseMaterialAdmin):
    ordering = ('-id',)
    form = ContestAdminForm
    social_card_fields = BaseMaterialAdmin.social_card_fields + ['w_image']
    readonly_fields = BaseMaterialAdmin.readonly_fields + ('_vote_list_field', )

    fieldsets = (
        (u'Статистика', {
            'fields': (
                ('views_cnt', 'vk_share_cnt', 'fb_share_cnt', 'tw_share_cnt', 'ok_share_cnt'),
            ),
        }),
        (u'Свойства', {
            'classes': ('lined',),
            'fields': ('is_hidden', 'is_blocked', 'user_can_add'),
        }),
        (u'Категории', {
            'fields': ('sites', 'type', 'project')
        }),
        (u'Число дня', {
            'classes': ('collapse',),
            'fields': ('is_number_of_day', 'number_of_day_number', 'number_of_day_text'),
        }),
        (u'Карточка для социальных сетей', {
            'classes': ('collapse',),
            'fields': ('social_image', 'social_text', 'social_label', 'social_card'),
        }),
        (None, {
            'fields': (
                'hide_comments', 'disable_comments', ('stamp', 'published_time'), ('date_start', 'date_end'), 'title',
                'slug', 'caption', 'content', 'w_image', 'image', 'image_caption', 'instagram_tag', 'tags',
            ),
        }),
        (u'Статистика голосов', {
            'fields': ('_vote_list_field', ),
        }),
    )

    inlines = [ParticipantInline]

    SHOW_VOTES_LIMIT = 50

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css', 'news/css/admin.css', 'contests/css/admin.css',),
        }
        js = (
            'news/js/admin.js', 'js/apps-js/admin.js', 'contests/js/admin.js',
        )

    def get_urls(self):
        return [
            url(r'^vote_list/(\d+)/$', self.admin_site.admin_view(self.vote_list)),
            url(r'^more_votes/(\d+)/$', self.admin_site.admin_view(self.more_votes)),
        ] + super(ContestAdmin, self).get_urls()

    @options(short_description=u'Участники', allow_tags=True)
    def _vote_list_field(self, contest):
        return mark_safe('<div id="vote-list"><button>Показать список</button></div>')

    def vote_list(self, request, contest_id):
        """
        Обрабочик ajax-запроса с кнопки Показать участников

        Возвращает отрендеренный html, который вставляется под кнопкой.

        Участников и голосов может быть очень много, поэтому по-умолчанию мы
        выводит по 50 голосов на участника + кнопку Показать еще. При ее нажатии
        вызывается вьюшка more_votes и выдает остатки.
        """
        contest = Contest.objects.get(pk=contest_id)
        participants = Participant.objects.filter(contest=contest)

        data = []
        for participant in participants:
            rating_object = participant.rating_object
            if not rating_object:
                # никто не голосовал за этого участника
                continue

            try:
                rates = Rate.objects.filter(obj=rating_object)\
                    .select_related('user__profile').prefetch_related('user__social_auth')\
                    .order_by('-user__date_joined')[:self.SHOW_VOTES_LIMIT]

                rates = list(rates)  # чтобы вызов len ниже не делал лишний sql-запрос

                votes = []
                for rate in rates:
                    user = rate.user
                    votes.append({
                        'full_name': user.get_full_name(),
                        'phone': user.profile.phone,
                        'date_joined': user.date_joined,
                        'socials': self._get_socials(user),
                    })

                # если в базе еще есть голоса, мы выведем кнопку Показать еще
                show_more = rating_object.total_sum - len(rates)

                if participant.user:
                    name = '%s %s' % (participant.user.first_name, participant.user.last_name)
                    username = participant.user.username
                else:
                    name = participant.title
                    username = None

                data.append({
                    'name': name,
                    'username': username,
                    'show_more': show_more,
                    'id': participant.pk,
                    'total_sum': rating_object.total_sum,
                    'votes': votes,
                })

            except (MultiValueDictKeyError, ObjectDoesNotExist):
                pass

        return render(request, 'contests/admin/vote_list.html', {'participants': data})

    def more_votes(self, request, participant_id):
        """
        Эта вьюшка вызывается при нажатии на кнопку Показать еще голоса
        """
        participant = Participant.objects.get(pk=participant_id)

        rates = Rate.objects.filter(obj=participant.rating_object)\
            .select_related('user__profile').prefetch_related('user__social_auth')\
            .order_by('-user__date_joined')[self.SHOW_VOTES_LIMIT:]

        votes = []
        for rate in rates:
            user = rate.user
            votes.append({
                'full_name': user.get_full_name(),
                'phone': user.profile.phone,
                'date_joined': user.date_joined,
                'socials': self._get_socials(user),
            })

        return render(request, 'contests/admin/vote_rows.html', {'votes': votes})

    def _get_socials(self, user):
        """
        Получить данные о соц сетях пользователя

        :type user: django.contrib.auth.models.User
        """

        socials = []
        for social in user.social_auth.all():
            if 'profile_url' in social.extra_data or 'screen_name' in social.extra_data:
                socials.append({
                    'url': social.extra_data.get('profile_url'),
                    'name': social.extra_data.get('screen_name'),
                })

        return socials


class ContestFilter(admin.SimpleListFilter):
    title = u'Конкурсы'
    parameter_name = 'contest'

    def lookups(self, request, model_admin):
        return Contest.objects.all().order_by('-id').values_list('id', 'title')

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            queryset = queryset.filter(contest=self.value())
        return queryset


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('_get_title', 'contest', 'is_active')
    list_select_related = True
    list_filter = (ContestFilter,)
    inlines = (GalleryInline,)
    ordering = ('-id',)
    readonly_fields = ('user',)

    @admin_media_static
    class Media(object):
        js = ('js/apps-js/admin.js', )

    @options(short_description=u'Участник')
    def _get_title(self, obj):
        return obj.full_name or obj.title or u'Пользователь @{}'.format(obj.username)

    def save_model(self, request, obj, form, change):
        old_obj = Participant.objects.filter(pk=obj.pk).first()

        super(ParticipantAdmin, self).save_model(request, obj, form, change)

        if change and (obj.contest.type == Contest.TYPE_PHOTO) and obj.is_active and obj.user and obj.user.email:
            tpl_notify(
                u'Ваша фотография успешно прошла модерацию',
                'contests/notif/participant_approve.html',
                {'participant': obj},
                emails=[obj.user.email, ]
            )
        elif change and (obj.contest.type == Contest.TYPE_PHOTO) and old_obj.reject_reason != obj.reject_reason \
                and obj.user and obj.user.email:
            tpl_notify(
                u'Ваша фотография не прошла модерацию',
                'contests/notif/participant_reject.html',
                {'participant': obj},
                emails=[obj.user.email, ]
            )
