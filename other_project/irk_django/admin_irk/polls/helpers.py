# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.polls import views


def poll_urls(app_label):
    """Урлы голосований для разделов"""

    return [
        # Голосования
        url(r'poll/(?P<poll_id>\d+)/$', views.read, {'app_label': app_label}, name='poll_read'),
    ]
