from django.conf.urls import  url

from djangoChat import views

urlpatterns = [
    # url(r'^$', views.index, name='index'), /// test aps
    url(r'^api/update$',views.chat_api,name='chat_api'),
    url(r'^api/new$',views.chat_api_new,name='chat_api'),
]