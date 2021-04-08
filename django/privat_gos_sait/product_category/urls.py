"""
URL Configuration
"""
from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from .views import ArticleListView ,post_list,article
urlpatterns = [
    path('',post_list),
    path('<slug>/',ArticleListView.as_view(),name='product_category_list'),
    path('<cat>/<slug>/',article),
]