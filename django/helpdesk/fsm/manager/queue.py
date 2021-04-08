from django.db import models
from django.contrib.auth.models import User

class SupportQManager(models.Manager):
    def get_root(self,user:User):
        groups = user.groups.all()
        pk_list = list(set([ i.pk  for i in self.filter(gr__in=groups,parent=None) ]))
        return self.filter(pk__in=pk_list)


class QueueSupportManagerTable(models.Manager):
    ## return quese
    ## return dosk
    ## return path
    ## return table
    def get_root_list(self,user):
        obj = {
            "name":"ИТДС",
            "sub": [
                { "name":"locki" ,"url":"#"},
                { "name":"tor","url":"#"},
                { "name":"ingris","url":"#"},
            ]
        }
        return [ obj,]

    def get_test_root(self,q,s):
        obj = [
            {"name":"test","id":1},
            {"name":"test","id":2},
        ]
        return obj

    def get_tables(self,queue,stream):
        obj = {
                "title":"f",
                "id":12,
                "thead": [
                    "test",
                    "fest",
                    "lock"
                ],
                "body_list":[
                    [
                        {"name":"test0"},
                        {"name":"test1"},
                        {"name":"test2"},
                        {
                            "name":"test3",
                            "is_button":True,
                            "button": [
                                {
                                 "name": "test1",
                                 "url": "#",
                                 "btn_style": "get"
                                },
                                {
                                 "name": "test1",
                                 "url": "#",
                                 "btn_style": "push"
                                },
                                {
                                 "name": "test1",
                                 "url": "#",
                                 "btn_style": "view"
                                },
                            ],
                        }
                        ]
                ],
                "tfoot":[
                    "test",
                    "fest",
                    "lock"
                ]
        }
        return [obj]

    def get_list(self,user,active_id):
        obj = {
            "title":"title",
            "dep":[
                {
                    "name":"test",
                    "url":"#"
                },
                {
                    "name":"test2",
                    "url":"#"
                },
            ]
        }
        return obj
