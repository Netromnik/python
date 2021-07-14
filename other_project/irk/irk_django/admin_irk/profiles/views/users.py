# -*- coding: utf-8 -*-

import warnings
import logging

from social_django.models import UserSocialAuth

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import user_passes_test

from irk.profiles.models import Profile, UserBanHistory
from irk.comments.permissions import is_moderator
from irk.utils.http import get_redirect_url, JsonResponse


logger = logging.getLogger(__name__)


def read(request, user_id):
    """Просмотр профиля отдельного пользователя"""

    profile = get_object_or_404(Profile, user_id=user_id)
    associations = UserSocialAuth.objects.filter(user=profile.user)

    try:
        association_vk = associations.get(provider='vk-oauth2')
    except UserSocialAuth.DoesNotExist:
        association_vk = None
    try:
        association_twitter = associations.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        association_twitter = None
    try:
        association_facebook = associations.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        association_facebook = None
    try:
        association_odnoklassniki = associations.get(provider='odnoklassniki-oauth2')
    except UserSocialAuth.DoesNotExist:
        association_odnoklassniki = None

    ban = None
    if is_moderator(request.user) and profile.is_banned:
        try:
            ban = UserBanHistory.objects.filter(user=profile.user).order_by('-created')[0]
        except IndexError:
            pass

    context = {
        'profile': profile,
        'is_moderator': is_moderator(request.user),
        'associations': associations,
        'can_edit': request.user == profile.user,
        'association_vk': association_vk,
        'association_twitter': association_twitter,
        'association_facebook': association_facebook,
        'association_odnoklassniki': association_odnoklassniki,
        'ban': ban
    }

    return render(request, 'profiles/users/read.html', context)


@user_passes_test(lambda u: u.has_perm('comments.change_comment'))
def avatar_remove(request, pk):
    # TODO: запросы должны быть только POST
    warnings.warn('Avatar removal request should be POST type', RuntimeWarning)

    profile = get_object_or_404(Profile, user_id=pk)
    if profile.image:
        profile.image.delete()

    if request.is_ajax():
        return JsonResponse({
            'status': 200,
        })

    return HttpResponseRedirect(get_redirect_url(request))
