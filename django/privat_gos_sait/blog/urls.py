from django.urls import path
from django.conf.urls import url, include


from . import views

urlpatterns = [
    path('', views.BlogListView.as_view(), name='home'),
    path('post/<int:pk>/', views.BlogDetailView.as_view(), name='post_detail'),
  #  url(r'^cart/', include('cart.urls')),
]
