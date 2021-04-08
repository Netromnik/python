from django.urls import path,include
from view.autch.login_logout import Login,Logout
from  .dasbord import Dasbord
from .table import Table
from .ticket_crud import TicketView,CreateTicket
import notifications.urls
from .analitic_page import admin_analitic
app_name = 'views'

urlpatterns = [
    path('login/',Login.as_view(),name="login"),
    path('logout/',Logout.as_view(next_page='/login/'),name="logout"),
    path('newticket/',CreateTicket.as_view(),name="CreateTicket"),
    path('ticket/<int:pk>/',TicketView.as_view(),name="detail_ticket"),
    path('<int:slug_query_pk>/<int:slug_sub_pk>/', Table.as_view(), name="router_table"),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('admin_analitic/',admin_analitic,name="analitic"),
    path('', Dasbord.as_view(), name="dasbord"),
]