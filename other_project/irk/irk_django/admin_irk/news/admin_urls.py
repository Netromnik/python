# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.news import admin_socpult as socpult
from irk.news import admin_views

urlpatterns = [
    url(r'^home_positions/$', admin_views.material_home_positions, name='admin_material_home_positions'),
    url(r'^home_positions/save/$', admin_views.material_home_positions_save, name='admin_material_home_positions_save'),
    url(r'^home_positions/other_materials/$', admin_views.home_other_materials, name='admin_material_other_materials'),
    url(r'^home_positions/stick_position/$', admin_views.material_set_stick_position,
        name='admin_material_set_stick_position'),

    url(r'^newsletter/daily/$', admin_views.newsletter_materials, {'period': 'daily'}, name='admin_daily_newsletter'),
    url(r'^newsletter/weekly/$', admin_views.newsletter_materials, {'period': 'weekly'},
        name='admin_weekly_newsletter'),
    url(r'^newsletter/other_materials/$', admin_views.newsletter_other_materials,
        name='admin_newsletter_other_materials'),
    url(r'^newsletter/save/$', admin_views.newsletter_save, name='admin_newsletter_save'),

    url(r'^articles/$', admin_views.article_index, name='admin_article_index'),
    url(r'^articles/save/$', admin_views.article_index_save, name='admin_article_index_save'),
    url(r'^articles/lock/$', admin_views.article_index_lock, name='admin_article_index_lock'),
    url(r'^articles/other_materials/$', admin_views.article_index_other, name='admin_article_index_other'),

    url(r'^social/(?P<alias>\w+)/post/(?P<material_id>\d+)/$', admin_views.social_post, name='admin_social_post'),
    url(r'^social/status/$', admin_views.social_post_status, name='admin_social_post_status'),
]

urlpatterns += [
    url(r'^social_pult/$', socpult.index, name='admin_social_pult'),
    url(r'^social_pult/upload/(?P<material_id>\d+)/$', socpult.upload, name='admin_social_pult_upload'),
    url(r'^social_pult/news/list/$', socpult.list_news, name='admin_social_pult_list_news'),
    url(r'^social_pult/scheduled/list/$', socpult.list_scheduled, name='admin_social_pult_list_scheduled'),
    url(r'^social_pult/editor/(?P<material_id>\d+)/$', socpult.load_editor, name='admin_social_pult_load_editor'),
    url(r'^social_pult/news/(?P<material_id>\d+)/publish/$', socpult.publish_post,
        name='admin_social_pult_publish_post'),
    url(r'^social_pult/save_draft/(?P<material_id>\d+)/$', socpult.save_draft, name='admin_social_pult_save_draft'),
    url(r'^social_pult/post/(?P<post_id>\d+)/$', socpult.view_post, name='admin_social_pult_view_post'),
]
