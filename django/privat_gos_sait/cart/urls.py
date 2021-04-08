from django.conf.urls import url

from . import views
from django.urls import path


app_name="cart"

urlpatterns = [
    path('remove/for/<product_id>/', views.CartRemove_for, name='CartRemove_for'),
    path('add/for/<product_id>/', views.CartAdd_for, name='CartAdd_for'),
    path('', views.CartDetail, name='CartDetail'),
    path('remove/<product_id>/', views.CartRemove, name='CartRemove'),
    path('add/<product_id>/', views.CartAdd, name='CartAdd'),
]
