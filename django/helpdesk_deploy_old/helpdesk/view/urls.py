from django.urls import path, include

from view.autch.login_logout import Login, Logout
from .dasbord import Dasbord
from .ticket_crud import TicketView, CreateTicket, TaskUpdate

app_name = 'views'

urlpatterns = [
    path('login/',Login.as_view(),name="login"),
    path('logout/',Logout.as_view(next_page='/login/'),name="logout"),
    path('newticket/',CreateTicket.as_view(),name="CreateTicket"),
    path('updateticket/<int:pk>/',TaskUpdate.as_view(),name="TaskUpdate"),
    path('ticket/<int:pk>/',TicketView.as_view(),name="detail_ticket"),
    path('<int:slug_query_pk>/<int:slug_stream_pk>/', include('view.s.urls')),
    path('', Dasbord.as_view(), name="dasbord"),
]

## /<type of vievs>/slug_query/slug_stream/ticket/<int:pk>/
    # path('ticket/<int:pk>/',DetailTask.as_view(),name="detail_ticket"),
#     path('newticket/',ContactView.as_view(),name="ContactView"),
#     # path('feed/', LatestEntriesFeed()),
#     path('kanbal/', KanbalDefault.as_view(), name="kanbal-defoult"),
#     path('kanbal/<int:slug_query_pk>/<int:slug_stream_pk>/', KanbalDefault.as_view(),name="kanbal"),
#     path('table/<int:slug_query_pk>/', Dasbord.as_view(), name="table"),
#     path('table/<int:slug_query_pk>/<int:slug_stream_pk>/', Dasbord.as_view(), name="table"),
#     path('<int:slug_query_pk>/<int:slug_stream_pk>/?/<int:pk>/', Dasbord.as_view(), name="s"),
