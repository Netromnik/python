from django.urls import path
from .views import  *
from django.conf.urls import url

urlpatterns = [
    url(r'^for_you.*/', my_view),
    path('<reder>/',post_list),
    path('<cat>/<slug>/',post_titile,name='detail'),
    ]

