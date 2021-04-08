from django.db.models.manager import Manager
class BaseWikiNodeManeger(Manager):

    def create_root(self,node_root):
        node_root.level = 0
        node_root.is_publish = True
        node_root.path = ""
        node_root.save()

    def get_roots(self):
        return self.filter(level=0)

    def mv(self, node ,parent ):
        if node.get_children().count() != 0:
            raise ValueError("delete children")
        else:
            node.parent_id = parent.id

class WikiNodeManeger(BaseWikiNodeManeger):

    def _creat_leaps(self,leaps):
        obj_leaps = {
            "title":leaps.title,
            "is_collapse":False,
            "url":leaps.url,
            "leaf": []
        }
        return obj_leaps

    def get_node_root(self):
        list_obj =  []
        for obj in self.get_roots():
            if obj.get_children().count() != 0:
                temp = {
            "title": obj.title,
            "is_collapse": True,
            "url": obj.url(),
            "leaf": [ self._creat_leaps(i)
                for i in obj.get_children_is_publish()
            ]
        }
            else:
                temp = self._creat_leaps(obj)
            list_obj.append(temp)
        return list_obj

    def get_not_publisk_node(self,user):

        temp = {
            "title": 'Неопубликованные',
            "is_collapse": True,
            "url": "#",
            "leaf": [self._creat_leaps(i)
                     for i in self.filter(author = user,is_publish =False)
                     ]
        }
        return temp

    def get_node_content(self,leaps_pk):
        obj = self.get(pk=leaps_pk)
        content = obj.content
        return content

    def get_write(self,user,pk):
        obj = self.get(pk=pk)
        if user == obj.author:
            return True
        if obj.get_perm(user) !=0:
            return True
        return False

    def get_materilize(self,pk):
        obj = self.get(pk = pk)
        obj_list = [ ]
        if obj.path == None:
            return [{
            "title": obj.title ,
            "url": obj.url()
            }, ]
        for i in obj.path.split(obj.delimiter):
            temp = self.get(pk = i)
            temp_obj = {
            "title": temp.title ,
            "url": temp.url()
            }
            obj_list.append(temp_obj)
        return obj_list