''' Django notification urls file '''
# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path('unread/', views.UnreadNotificationsList.as_view(), name='unread'),
    path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('mark-as-read/<int:slug_mark>/', views.mark_as_read, name='mark_as_read'),
    path('mark-as-unread/<int:slug_notif>/', views.mark_as_unread, name='mark_as_unread'),
    path('delete/<slug:slug_notif>/', views.delete, name='delete'),
    path('api/unread_count/', views.live_unread_notification_count, name='live_unread_notification_count'),
    path('api/all_count/', views.live_all_notification_count, name='live_all_notification_count'),
    path('api/unread_list/', views.live_unread_notification_list, name='live_unread_notification_list'),
    path('api/unread_list_push/', views.live_unread_notification_list_push, name='live_unread_notification_list'),
    path('api/all_list/', views.live_all_notification_list, name='live_all_notification_list'),
    path('', views.AllNotificationsList.as_view(), name='all'),
]

app_name = 'notifications'

