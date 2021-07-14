# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.authentication.views import socials

app_name = 'authentication_social'

urlpatterns = [
    url(r'^error/$', socials.error, name='error'),
    url(r'^error-inactive/$', socials.error_inactive, name='error_inactive'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<user_id>\d+)/(?P<association_id>\d+)/$', socials.disconnect,
        name='disconnect'),
]
