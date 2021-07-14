from django.conf.urls import url

from adv import admin_views as views


urlpatterns = [
    url(r'^stat/$', views.place_stat, name='admin_adv_place_stat'),
    url(r'^places.json$', views.places_json, name='admin_adv_places_json'),
]
