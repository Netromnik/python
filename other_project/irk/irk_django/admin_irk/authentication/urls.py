# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from irk.authentication.views import remind, register, user
from irk.profiles.views import auth

app_name = 'authentication'

register_urlpatterns = (
    [
        url(r'^$', register.index, name='index'),
        url(r'^details/$', register.details, name='details'),
        url(r'^confirm-email/$', register.confirm_email, name='confirm_email'),
        url(r'^success/$', register.success, name='success'),
        url(r'^success/check-avatar/$', register.check_avatar_load, name='check_avatar_load'),
    ], 'register'
)

profile_urlpatterns = (
    [
        url(r'^$', user.update, name='update'),
        url(r'^password/$', user.update_password, name='password'),
    ], 'profile'
)

urlpatterns = [
    url(r'^login/$', user.login, name='login'),
    url(r'^logout/$', user.logout, name='logout'),
    url(r'^remind/$', remind.index, name='remind'),

    url(r'^register/', include(register_urlpatterns)),
    url(r'^profile/', include(profile_urlpatterns)),

    url(r'^change/$', auth.change, name='change'),
    url(r'^unsubscribe/$', auth.unsubscribe, name='unsubscribe'),
]
