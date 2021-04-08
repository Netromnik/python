from django.contrib import admin
from django.urls import path,include
from  .views import *
urlpatterns = [
    path('',My_list_views.as_view()),
    path('list/news/',my_rederect),
    path('list/<slug>/',DetailView),
]
