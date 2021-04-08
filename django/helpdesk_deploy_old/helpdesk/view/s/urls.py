from django.urls import path

from .kanban import KanbalDefault
from .resolve import router
from .table import Table

app_name = 'router'

urlpatterns = [
    path('', router, name="router"),
    path('table/', Table.as_view(), name="router_table"),
    path('kanban/', KanbalDefault.as_view(), name="router_kanban"),
]
