from fsm.models import Task
import django_tables2 as tables
from .coll import NonSubscriteTaskButton,TaskActiveButton,AdminButton,TimeDateColl
from django.db.models import Avg
from datetime import datetime

class GeneralTable(tables.Table):
    pagin_name = ""
    title_h = ""
    # data_update = TimeDateColl()
    class Meta:
        model = Task
        template_name = "tables/template_task_table.html"
        fields = ("pk","title","queue","data_update","state", )
        row_attrs = {
            "class": lambda record: record.the_importance
        }
        order_by = "-pk"

class ActiveTask(GeneralTable):
    id = TaskActiveButton(verbose_name="")
    pagin_name = "active_table"
    title_h = "Активные заявки"
    class Meta:
        model = Task
        template_name = "tables/template_task_table.html"
        fields = ("pk","title","queue","owner","data_update","state","id" )
        row_attrs = {
            "class": lambda record: record.the_importance
        }
        order_by = "-pk"

class NotActiveTask(GeneralTable):
    id = NonSubscriteTaskButton(verbose_name="")
    pagin_name = "not_active_table"
    title_h = "Заявки без исполнителя"
    class Meta:
        model = Task
        template_name = "tables/template_task_table.html"
        fields = ("pk","title","queue","owner","data_update","state","id" )
        row_attrs = {
            "class": lambda record: record.the_importance
        }
        order_by = "-pk"

class AdminTask(GeneralTable):
    id = AdminButton(verbose_name="")
    pagin_name = "admin_table"
    title_h = "Все заявки"

    # def get_top_pinned_data(self):
    #     return [{
    #         "pk":"Итог  {}".format(self.data.data.count()),
    #         "data_create":  datetime(9999, 12, 12, 0, 0, 0, 0),
    #         "data_update": datetime(9999, 12, 12, 0, 0, 0, 0),
    #         "raiting":self.data.data.filter(raiting__gt =-1).aggregate(Avg('raiting'))["raiting__avg"],
    #         "state":self.stat_task(self.data.data),
    #     }]
    # def stat_task(self,q):
    #     q_list = [
    #            q.filter(state="Открыта").count(),
    #            q.filter(state="Ваполняется").count(),
    #            q.filter(state="Решена").count(),
    #            q.filter(state="Закрыта").count()
    #     ]
    #     return "/".join(str(x) for x in q_list)

    class Meta:
        model = Task
        template_name = "tables/template_task_table.html"
        fields = ("pk","title","queue","data_create","data_update","state","queue","raiting","owner","responsible","id" )
        row_attrs = {
            "class": lambda record: record.the_importance
        }
        order_by = "-pk"
