# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.gallery import views

app_name = 'gallery'

urlpatterns = [
    url(r'^admin_multiupload/$', views.admin_multiupload_handler, name='admin_multiupload_handler'),
    url(r'^multiupload/$', views.multiupload_handler, name='multiupload_handler'),
    url(r'^delete/$', views.delete_image, name='delete_image'),
    url(r'^main/$', views.main_image, name='main_image'),
    url(r'^best/$', views.best_image, name='best_image'),
    url(r'^watermark/$', views.set_watermark, name='set_watermark'),
    url(r'^watermark_all/$', views.set_watermark_all, name='set_watermark_all'),
]
