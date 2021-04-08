from fsm.models import  Task,Queue
from mixin.generic_viev.page import Page ,BreadcrumbItem

class Dasbord(Page):
    title = "Дашборд"
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=True,url="/") ,]
    template_name = "locations/dasbord.html"
    context_object_name = "obj"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["static_data"] = Task.statistic_data_manager.stats(self.request.user)
        kwargs["raiting"] = Task.statistic_data_manager.get_raiting(self.request.user)
        kwargs["alert_all"] = self.request.user.notifications.unread()
        kwargs["table"] = Task.object.filter(owner = self.request.user)
        kwargs["cart_all"] = Queue.support_manager.get_root(self.request.user)
        return  kwargs

# get t/1/1 -> all to task 1,1
# get t/-1/-1 -> all to task 0,1