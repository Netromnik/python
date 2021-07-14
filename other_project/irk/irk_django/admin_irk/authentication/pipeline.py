# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from social_core.pipeline.partial import partial

from irk.authentication import settings as app_settings
from irk.authentication.tasks import load_user_avatar
from irk.profiles.models import Profile


@partial
def get_username(strategy, details, backend, user=None, *args, **kwargs):
    """Элемент `settings.SOCIAL_AUTH_PIPELINE` для ввода логина и email новому пользователю"""

    session = backend.strategy.session

    if not session.get('auth_username') and user is None:
        form_initial = {
            'username': None,
            'email': None,
        }
        backend = backend.name

        if backend == 'twitter':
            form_initial['username'] = kwargs['response']['screen_name']
        elif backend == 'facebook':
            form_initial['username'] = kwargs['response'].get('name', '')
            email = kwargs['response'].get('email', '')
            if '@facebook.com' not in email:
                form_initial['email'] = email
        elif backend == 'vk-oauth2':
            form_initial['username'] = u' '.join([kwargs['response']['first_name'], kwargs['response']['last_name']])
        elif backend == 'odnoklassniki-oauth2':
            form_initial['username'] = u' '.join([kwargs['response']['first_name'], kwargs['response']['last_name']])

        # В качестве отображаемого имени пользователя теперь всегда используется username
        form_initial['name'] = form_initial['username']

        session[app_settings.SOCIAL_SESSION_KEY] = form_initial
        session[app_settings.CONFIRM_SESSION_KEY] = 'social'

        current_partial = kwargs.get('current_partial')

        return strategy.redirect('{}?partial_token={}'.format(reverse('authentication:register:details'),
                                                              current_partial.token))


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    session = backend.strategy.session

    if user:
        # Убеждаемся, что пользователь верифицирован
        Profile.objects.filter(user=user).update(is_verified=True)
        return {
            'user': user,
            'is_new': False,
        }

    username = session.get('auth_username')
    email = session.get('auth_email')
    name = session.get('auth_name')

    user = User(username=username, email=email)
    user.set_unusable_password()
    user.save()

    if not Profile.objects.filter(user=user).exists():
        profile = Profile(user=user, full_name=name)
        profile.is_verified = True  # Пользователь зашел через соцсеть, считаем, что он действительно человек
        profile.save()

    session.pop('auth_username', None)
    session.pop('auth_email', None)
    session.pop('auth_details_initial', None)

    return {
        'user': user,
        'is_new': True,
    }


def load_extra_data(strategy, details, backend, response, uid, user, request, is_new=False, *args, **kwargs):
    social = kwargs.get('social')
    if not social:
        return

    task = None

    if social.provider == 'twitter':
        profile_url = 'http://twitter.com/{0}'.format(response['screen_name'])
        screen_name = response['screen_name']
        if is_new:
            task = load_user_avatar.delay(user.id, response['profile_image_url'])

    elif social.provider == 'vk-oauth2':
        profile_url = 'http://vk.com/{0}'.format(response['screen_name'])
        screen_name = response['screen_name']
        if is_new:
            task = load_user_avatar.delay(user.id, response['photo'])

    elif social.provider == 'facebook':
        profile_url = response.get('link', '')
        if not profile_url:
            profile_url = 'https://www.facebook.com/profile.php?id={0}'.format(response['id'])
        screen_name = response.get('username', '')
        if not screen_name:
            screen_name = response.get('name', '')
        if is_new:
            task = load_user_avatar.delay(user.id, response['picture']['data']['url'])

    elif social.provider == 'odnoklassniki-oauth2':
        profile_url = 'http://ok.ru/profile/{}/'.format(response['uid'])
        screen_name = response.get('name', '')
        if is_new:
            task = load_user_avatar.delay(user.id, response['pic_3'])

    else:
        raise ImproperlyConfigured('Unknown backend for profile URL resolving: {0}'.format(social.provider))

    if task:
        session = backend.strategy.session
        session[app_settings.AVATAR_LOADING_TASK_SESSION_KEY] = task.id

    social.extra_data['profile_url'] = profile_url
    social.extra_data['screen_name'] = screen_name
    social.save()

    return {'social': social}


def ensure_user_active(strategy, details, backend, user, response, *args, **kwargs):
    """
    Элемент `settings.SOCIAL_AUTH_PIPELINE`

    После авторизации пользователя в соцсетях, может случиться, что у нас юзер
    is_active=False. В этом случае мы прервем цепочку и переадресуем на страничку
    с ошибкой.
    """

    if user and not user.is_active:
        url = reverse('authentication_social:error_inactive')
        return strategy.redirect('{}?user={}'.format(url, user.id))
