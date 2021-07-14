# -*- coding: utf-8 -*-

from irk.pages import views

urlpatterns = [
    (r'^(?P<url>.*)$', views.flatpage),
]
