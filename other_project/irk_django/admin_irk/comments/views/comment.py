# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import time
import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.conf import settings

from irk.blogs.models import BlogEntry
from irk.comments.forms import CommentCreateForm, CommentEditForm
from irk.comments.helpers import CommentSpamChecker
from irk.comments.models import Comment, ActionLog
from irk.comments.permissions import get_email_moderators, get_afisha_email_moderators, is_moderator
from irk.comments.user_options import CommentsSortOption
from irk.obed.models import Establishment
from irk.phones.models import Firms
from irk.ratings.models import RatingObject
from irk.utils.helpers import get_client_ip, int_or_none, iptoint
from irk.utils.http import require_ajax, JsonResponse
from irk.utils.notifications import tpl_notify
from irk.utils.views.mixins import AjaxMixin, PaginateMixin


class CommentListView(PaginateMixin, View):
    """
    Список комментариев.

    2х уровневая система комментов
    Пагинация
    Сортировка
    10 лучших по рейтингу
    """

    ajax_template = 'comments/comment/list.html'

    @method_decorator(require_ajax)
    def get(self, *args, **kwargs):
        self._show_hidden = is_moderator(self.request.user)

        self._parse_params()

        context = self.get_context()

        return render(self.request, self.ajax_template, context)

    def get_context(self):
        ct_id = self.kwargs.get('ct_id')
        target_id = self.kwargs.get('target_id')
        target = self.parse_target(ct_id, target_id)

        qs = self.get_queryset(target)
        comments = self.sort(qs)
        self.set_sort_user_option()
        # comments, page_info = self._paginate(qs)

        return {
            'comments': self.as_tree(comments),
            # 'page_info': page_info,
            'request': self.request,
            'ct_id': ct_id,
            'object': target,
            'sort': self.sorting,
            'is_moderator': self._show_hidden,
        }

    def set_sort_user_option(self):
        comment_sort_options = CommentsSortOption(self.request)
        comment_sort_options.value = self.sorting
        comment_sort_options.save()

    def parse_target(self, ct_id, target_id):
        try:
            ct = ContentType.objects.get_for_id(ct_id)
            target = ct.get_object_for_this_type(pk=target_id)
        except ObjectDoesNotExist:
            raise Http404('Target is not exist!')
        else:
            return target

    def get_queryset(self, target):
        qs = Comment.objects.for_object(target).roots()

        if not self._show_hidden:
            qs = qs.visible()
        return qs

    def sort(self, queryset):
        if self.sorting == 'top':
            # Сортировка комментариев по количеству голосов

            comment_ct = ContentType.objects.get_for_model(Comment)

            comment_ids = list(queryset.values_list('id', flat=True))
            rate_objs = RatingObject.objects.filter(content_type=comment_ct, object_pk__in=comment_ids)

            rate_map = {}
            for rate_obj in rate_objs:
                rate_map[rate_obj.object_pk] = rate_obj.total_cnt

            comments = []
            for comment in queryset:
                try:
                    comment.popularity = rate_map[comment.pk]
                except KeyError:
                    comment.popularity = 0
                comments.append(comment)
            return sorted(comments, key=lambda k: k.popularity, reverse=True)

        elif self.sorting == 'asc':
            return queryset.order_by('created')
        else:
            return queryset.order_by('-created')

    def as_tree(self, comments):
        """Return two-level tree"""

        for comment in comments:
            comment.children = comment.get_descendants()

        return comments

    def _parse_params(self):
        # Pagination params
        start_index = int_or_none(self.request.GET.get('start')) or self.start_index
        self.start_index = max(start_index, 0)
        page_limit = int_or_none(self.request.GET.get('limit')) or self.page_limit_default
        self.page_limit = min(page_limit, self.page_limit_max)

        # Sorting params
        self.sorting = self.request.GET.get('sort', 'asc')


class CommentChildrenListView(View):
    ajax_template = 'comments/comment/children.html'

    @method_decorator(require_ajax)
    def get(self, *args, **kwargs):
        context = self.get_context()

        return render(self.request, self.ajax_template, context)

    def get_context(self):
        self._show_hidden = is_moderator(self.request.user)
        comment = self.parse_comment()

        qs = self.get_queryset(comment)

        return {
            'is_moderator': self._show_hidden,
            'comments': qs,
            'request': self.request,
            'object': comment.target,
        }

    def parse_comment(self):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, pk=comment_id)

    def get_queryset(self, comment):
        qs = comment.get_descendants()

        if not self._show_hidden:
            qs = qs.visible()
        return qs.order_by('created')


class CommentCreateView(AjaxMixin, View):
    """
    Создание комментария.
    """

    comment_template = 'comments/comment/list_item.html'

    def post(self, *args, **kwargs):
        target = self.parse_target()
        if not target:
            return {'ok': False, 'msg': 'Target does not exist!'}

        if not self.request.user.is_authenticated:
            return {'ok': False, 'msg': 'User does not authenticated'}

        if not self.has_permission(target):
            return {'ok': False, 'msg': 'Target cannot be commented on'}

        comment, err = self.create_comment(target)
        if err:
            return {'ok': False, 'msg': 'Error creating comment', 'errors': err}

        self.send_notifications(target, comment)

        context = {
            'is_moderator': is_moderator(self.request.user),
            'comment': comment,
            'request': self.request,
        }

        return {
            'ok': True,
            'msg': 'Comment is created',
            'html': render_to_string(self.comment_template, context),
            'comment_id': comment.pk,
            'comment_created_time': comment.created_timestamp,
            'comment_end_edit_time': comment.end_edit_timestamp,
        }

    def parse_target(self):
        ct_id = self.request.json.get('ct_id')
        target_id = self.request.json.get('target_id')

        try:
            ct = ContentType.objects.get_for_id(ct_id)
            target = ct.get_object_for_this_type(pk=target_id)
        except ObjectDoesNotExist:
            return None
        else:
            return target

    def has_permission(self, target):
        """Checks the target for the ability to comment by current user"""

        # User is banned
        if self.request.user.profile.is_ban():
            return False

        # User hasn't permissions
        # TODO: this

        # Target cannot be commented
        if hasattr(target, 'can_commented') and not target.can_commented:
            return False

        return True

    def create_comment(self, target):
        """Create new comment"""

        form = CommentCreateForm(self.request.json)
        if form.is_valid():

            # Проверка на спам
            spam_checker = CommentSpamChecker(self.request, form.instance.text)
            if spam_checker.check():
                return None, 'Message contains spam'

            comment = form.save(commit=False)
            comment.user = self.request.user
            comment.target = target
            comment.ip = iptoint(get_client_ip(self.request))
            comment.save()
            form.save_m2m()
            return comment, None
        else:
            return None, form.errors

    def send_notifications(self, target, comment):
        """Send all notifications"""

        self.send_moderator_notifications(target, comment)

        if comment.parent:
            self.send_answer_notifications(comment)

        # Уведомления о новых комментах в блоге для аторов блога
        if isinstance(target, BlogEntry):
            blog_author_id = target.author.pk
            if blog_author_id != comment.user.pk and not (comment.parent and blog_author_id == comment.parent.user.pk):
                self.send_blog_author_notifications(target, comment)

        # Уведомления о новых комментах для заведений обеда
        if isinstance(target, Firms):
            if Establishment.objects.filter(pk=target.pk).exists():
                self.send_establishment_notifications(target, comment)

    def send_blog_author_notifications(self, entry, comment):
        """Send notifications to moderators"""

        title = 'Новый комментарий к записи "{}"'.format(entry.title)
        emails = [entry.author.email, ]

        tpl_notify(
            title, 'comments/comment/notif/created.html', {'comment': comment, 'hide_delete_link': True},
            request=self.request, emails=emails,
        )

    def send_establishment_notifications(self, establishment, comment):
        """Send notifications to establishment owners"""

        title = 'Новый комментарий к заведению "{}"'.format(establishment.name)
        emails = [establishment.mail, ]

        tpl_notify(
            title, 'comments/comment/notif/created.html', {'comment': comment, 'hide_delete_link': True},
            request=self.request, emails=emails,
        )

    def send_moderator_notifications(self, target, comment):
        """Send notifications to moderators"""

        target_ct = ContentType.objects.get_for_model(target)

        title = 'Новый комментарий #{}'.format(target_ct.app_label)
        emails = tuple(get_email_moderators().values_list('email', flat=True))

        # Уведомления модераторам афиши
        if target_ct.app_label == 'afisha':
            emails = emails + tuple(get_afisha_email_moderators().values_list('email', flat=True))

        tpl_notify(
            title, 'comments/comment/notif/created.html', {'comment': comment}, request=self.request, emails=emails,
            sender='comments@irk.ru'
        )

    def send_answer_notifications(self, comment):
        """Send notifications to parent comment user"""

        parent_comment = comment.parent

        email = parent_comment.user.email

        if email and parent_comment.user.profile.comments_notify:
            title = 'Ответ на ваше сообщение на сайте Ирк.ру'
            tpl_notify(
                title, 'comments/comment/notif/answered.html', {'comment': comment, 'parent_comment': parent_comment},
                request=self.request, emails=[email, ],
            )

class CommentEditView(AjaxMixin, View):
    """
    Редактирование комментария.
    """

    comment_template = 'comments/comment/list_item.html'

    def post(self, *args, **kwargs):
        comment = self.get_comment()
        if not comment:
            return {'ok': False, 'msg': 'Message does not exist!'}

        if not self.request.user.is_authenticated:
            return {'ok': False, 'msg': 'User does not authenticated'}

        if not self.has_permission(comment):
            return {'ok': False, 'msg': 'Message cannot be edited'}

        comment, err = self.edit_comment(comment)
        if err:
            return {'ok': False, 'msg': 'Error editing comment', 'errors': err}

        self.send_notifications(comment)

        context = {
            'is_moderator': is_moderator(self.request.user),
            'comment': comment,
            'request': self.request,
        }

        return {
            'ok': True,
            'msg': 'Comment is updated',
            'html': render_to_string(self.comment_template, context),
            'comment_id': comment.pk
        }

    def get_comment(self):
        comment_id = self.kwargs['comment_id']
        return Comment.objects.filter(pk=comment_id).first()

    def has_permission(self, comment):
        # User is banned
        if self.request.user.profile.is_ban():
            return False

        # Нельзя редактировать комментарии на которые уже ответили
        if comment.get_visible_children_count() > 0:
            return False

        if comment.user.pk == self.request.user.pk \
            and comment.created >= datetime.datetime.now() - datetime.timedelta(seconds=settings.COMMENTS_EDIT_ALLOWED_TIME):
            return True
        return False

    def edit_comment(self, comment):
        """Edit comment"""

        form = CommentEditForm(self.request.json, instance=comment)
        if form.is_valid():

            # Проверка на спам
            spam_checker = CommentSpamChecker(self.request, form.instance.text)
            if spam_checker.check():
                return None, 'Message contains spam'

            comment = form.save(commit=False)
            comment.is_edited = True
            comment.save()
            return comment, None
        else:
            return None, form.errors

    def send_notifications(self, comment):
        """Send all notifications"""

        self.send_moderator_notifications(comment.target, comment)

    def send_moderator_notifications(self, target, comment):
        """Send notifications to moderators"""

        target_ct = ContentType.objects.get_for_model(target)

        title = 'Отредактирован комментарий #{}'.format(target_ct.app_label)
        emails = tuple(get_email_moderators().values_list('email', flat=True))

        # Уведомления модераторам афиши
        if target_ct.app_label == 'afisha':
            emails = emails + tuple(get_afisha_email_moderators().values_list('email', flat=True))

        tpl_notify(
            title, 'comments/comment/notif/created.html', {'comment': comment}, request=self.request, emails=emails,
            sender='comments@irk.ru'
        )


class CommentTextView(AjaxMixin, View):
    """Получить исходный текст для редактирования комментария"""

    def get(self, *args, **kwargs):
        comment = self.get_comment()
        if not comment:
            return {'ok': False, 'msg': 'Message does not exist!'}

        if not self.request.user.is_authenticated:
            return {'ok': False, 'msg': 'User does not authenticated'}

        if not self.has_permission(comment):
             return {'ok': False, 'msg': 'Getting text is not allowed'}

        return {
            'ok': True,
            'text': comment.text,
            'comment_id': comment.pk,
            'comment_created_time': comment.created_timestamp,
            'comment_end_edit_time': comment.end_edit_timestamp,
        }

    def get_comment(self):
        comment_id = self.kwargs['comment_id']
        return Comment.objects.filter(pk=comment_id).first()

    def has_permission(self, comment):

        if self.request.user.profile.is_ban():
            return False

        if comment.user.pk != self.request.user.pk:
            return False

        return True


class CommentUserDeleteView(AjaxMixin, View):

    def post(self, *args, **kwargs):
        comment = self.get_comment()
        if not comment:
            return {'ok': False, 'msg': 'Message does not exist!'}

        if not self.request.user.is_authenticated:
            return {'ok': False, 'msg': 'User does not authenticated'}

        if not self.has_permission(comment):
            return {'ok': False, 'msg': 'Message cannot be change the status'}

        self.delete_comment(comment)

        return {'ok': True, 'msg': 'The comment has been deleted'}

    def get_comment(self):
        comment_id = self.kwargs['comment_id']
        return Comment.objects.filter(pk=comment_id).first()

    def has_permission(self, comment):
        # User is banned
        if self.request.user.profile.is_ban():
            return False

        # Нельзя удалять комментарии на которые уже ответили
        if comment.get_visible_children_count() > 0:
            return False

        if comment.user.pk == self.request.user.pk \
            and comment.created >= datetime.datetime.now() - datetime.timedelta(seconds=settings.COMMENTS_EDIT_ALLOWED_TIME):
            return True
        return False

    def delete_comment(self, comment):
        comment.status = Comment.STATUS_DIRECT_DELETE
        comment.save()
        ActionLog.objects.create(action=ActionLog.ACTION_DELETE, user=self.request.user, comment=comment)
        return comment


class CommentToggleView(View):
    """Toggle comment status"""

    def get(self, *args, **kwargs):
        """Удаление по GET запросам используется для писем"""
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        comment = self.get_comment()
        if not comment:
            return JsonResponse({'ok': False, 'msg': 'Message does not exist!'})

        if not self.request.user.is_authenticated:
            return JsonResponse({'ok': False, 'msg': 'User does not authenticated'})

        if not self.has_permission():
            return JsonResponse({'ok': False, 'msg': 'Message cannot be change the status'})

        comment = self.toggle_comment(comment)
        self.toggle_descendants(comment)

        self.send_notifications(comment)

        if self.request.is_ajax():
            return JsonResponse({'ok': True, 'msg': 'The comment changed the status'})
        else:
            return redirect(comment.get_absolute_url())

    def get_comment(self):
        comment_id = self.kwargs['comment_id']
        return Comment.objects.filter(pk=comment_id).first()

    def has_permission(self):
        """Checks the target for the ability to change status comment by current user"""

        return is_moderator(self.request.user)

    def send_notifications(self, comment):
        raise NotImplementedError

    def toggle_comment(self, comment):
        raise NotImplementedError

    def toggle_descendants(self, comment):
        raise NotImplementedError


class CommentDeleteView(CommentToggleView):
    """Delete comment"""

    def toggle_comment(self, comment):
        comment.status = Comment.STATUS_DIRECT_DELETE
        comment.save()
        ActionLog.objects.create(action=ActionLog.ACTION_DELETE, user=self.request.user, comment=comment)
        return comment

    def toggle_descendants(self, comment):
        comments = comment.get_descendants()
        for comment in comments:
            if comment.status == Comment.STATUS_VISIBLE:
                comment.status = Comment.STATUS_AUTO_DELETE
                comment.save()
                ActionLog.objects.create(action=ActionLog.ACTION_DELETE, user=self.request.user, comment=comment)

    def send_notifications(self, comment):
        """Send notifications to user"""

        email = comment.user.email
        if email and comment.user.profile.comments_notify:
            title = 'Ваше сообщение на сайте Ирк.ру удалено модератором'
            tpl_notify(
                title, 'comments/comment/notif/deleted.html', {'comment': comment}, request=self.request,
                emails=[email, ],
            )


class CommentRestoreView(CommentToggleView):
    """Restore comment"""

    def toggle_comment(self, comment):
        comment.status = Comment.STATUS_VISIBLE
        comment.save()
        ActionLog.objects.create(action=ActionLog.ACTION_RESTORE, user=self.request.user, comment=comment)
        return comment

    def toggle_descendants(self, comment):
        comments = comment.get_descendants()
        for comment in comments:
            if comment.status == Comment.STATUS_AUTO_DELETE:
                comment.status = Comment.STATUS_VISIBLE
                comment.save()
                ActionLog.objects.create(action=ActionLog.ACTION_RESTORE, user=self.request.user, comment=comment)

    def send_notifications(self, comment):
        pass


@require_ajax
def history(request, comment_id):
    """История удалений/восстановлений комментаривев"""

    if not is_moderator(request.user):
        return HttpResponseForbidden()

    context = {
        'history': get_list_or_404(ActionLog, comment_id=comment_id)
    }

    return render(request, 'comments/comment/comment_history.html', context)
