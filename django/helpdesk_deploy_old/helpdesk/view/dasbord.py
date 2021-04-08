from base.models import Task ,LogHistory, Queue
from mixin.generic_viev.page import Page ,BreadcrumbItem
# create 3 set
#           -1 set autor
#           -2 set unsignet
#           -3 set user signet


class Dasbord(Page):
    title = "Дашборд"
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=True,url="/") ,]
    template_name = "locations/dasbord.html"
    context_object_name = "obj"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["static_data"] = Task.manager_user_self.stats(self.request.user)
        kwargs["alert_all"] = LogHistory.alert_manager.get_alert_user(self.request.user)
        kwargs["table"] = Task.manager_user_self.is_avtor(self.request.user)
        kwargs["cart_all"] = Queue.support_manager_table.get_root_list(self.request.user)
        return  kwargs

# get t/1/1 -> all to task 1,1
# get t/-1/-1 -> all to task 0,1