from django.contrib import admin
from django.urls import path,include
from fsm.button_api.common import open_start, sucefful,re_open,close
from fsm.button_api.rating import rating
from table_api.api_table import user_save_table,user_get_table

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('view.urls',namespace="view")),
    path('^inbox/notifications/', include("notifications.urls", namespace='notifications')),
    path('ticket/api/<int:task_pk>/up/', open_start, name="start_task"),
    path('ticket/api/<int:task_pk>/ok/', sucefful, name="successful_task"),
    path('ticket/api/<int:task_pk>/re_open/', re_open, name="reopen"),
    path('ticket/api/<int:task_pk>/close/', close, name="close_task"),
    path('ticket/api/<int:task_pk>/raiting/<int:raiting>/', rating, name="raiting_task"),
    path('chat/', include('djangoChat.urls')),
    ## table
    path("table/<slug:table_id>/create/",user_save_table),
    path("table/<slug:table_id>/get/",user_get_table),
]
