from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from base.models import Task


# obj = {
#         "title":"f",
#         "id":12,
#         "thead": [
#             "test",
#             "fest",
#             "lock"
#         ],
#         "body_list":[
#             [
#                 {"name":"test0"},
#                 {"name":"test1"},
#                 {"name":"test2"},
#                 {
#                     "name":"test3",
#                     "is_button":True,
#                     "button": [
#                         {
#                          "name": "test1",
#                          "url": "#",
#                          "btn_style": "get"
#                         },
#                         {
#                          "name": "test1",
#                          "url": "#",
#                          "btn_style": "push"
#                         },
#                         {
#                          "name": "test1",
#                          "url": "#",
#                          "btn_style": "view"
#                         },
#                     ],
#                 }
#                 ]
#         ],
#         "tfoot":[
#             "test",
#             "fest",
#             "lock"
#         ]
# }
class BasicTable:
    # static param
    tempalte_name = ""
    title = ""

    # dinamic param
    id = ""
    button = []
    th =  [
        "id",
        "stream",
        "title",
        "status",
        "autors",
        "created_at",
        "date_due",
        "updated_at",
    ]
    tfoot = []
    row = []
    def _get_thead(self):
         return [ _(getattr(Task,i).field.verbose_name.capitalize()) for i in self.th]

    def _get_tfoot(self):
        pass

    def _get_button(self,obj):
        pass

    def _create_row(self,data):
        row_list = []
        for obj in data:
            row = [ {"name":getattr(obj,i)} for i in self.th if i != "status"]
            row.insert(3,{"name":obj.get_status})
            row.append({"name":"test","is_button": True,"button":self._get_button(obj)})
            row_list.append(row)
        return row_list

    def __init__(self,data,id):
        self.id = id
        self.thead = self._get_thead()
        self.tfoot = self._get_tfoot()
        self.row = self._create_row(data)

    def _context_data(self,**kwargs):
        pass

    def get_table_html(self):
        pass


class TableAsignet(BasicTable):
    tempalte_name = "snippet/table/asignet_to.html"
    title = "Заявки выполняемые вами"

    def _get_tfoot(self):
        return self._get_thead()

    def _get_button(self,obj):
        button = [
                {
                    "name": "Посмотреть",
                    "url": obj.get_view_url(),
                    "btn_style": "view"
                },
        ]
        return button


    def _context_data(self,**kwargs):
        kwargs["title"] = self.title
        kwargs["id"] = self.id
        kwargs["thead"] = self.thead
        kwargs["tfoot"] = self.tfoot
        kwargs["rows"] = self.row
        return kwargs

    def get_table_html(self):
        kwargs   = self._context_data()
        template = get_template(self.tempalte_name)
        html     = template.render(context=kwargs)
        return html

class TableNonAsignet(TableAsignet):
    title = "Заявки на выполнения"
    th =  [
        "id",
        "stream",
        "title",
        "autors",
        "created_at",
        "date_due",
        "updated_at",
    ]
    def _create_row(self,data):
        row_list = []
        for obj in data:
            row = [ {"name":getattr(obj,i)} for i in self.th ]
            row.append({"name":"test","is_button": True,"button":self._get_button(obj)})
            row_list.append(row)
        return row_list

    def _get_button(self,obj):
        button = [
                {
                    "name": "Посмотреть",
                    "url": obj.get_view_url(),
                    "btn_style": "view"
                },
                {
                    "name": "Взять",
                    "url": "?event=get&id="+str(obj.id),
                    "btn_style": "view"
                },
        ]
        return button

