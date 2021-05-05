from django.test import TestCase
from core.models import CustomUser, TreeCategory
from django.core.serializers import serialize
import json

class AnimalTestCase(TestCase):
    def setUp(self):
        for i in range(9):
            obj = CustomUser(
                username=f'{i}_bot',
                email=f'{i}@mail.ru',
                phone=f"+7{i}242909968"
            )
            obj.set_password(str(i) + "test_password")
            obj.save()
        root = TreeCategory.add_root(
            name=f'rot_category'
        )
        root.users.add(
            *CustomUser.objects.all()
        )
        root.save()
        root2 = TreeCategory.add_root(
            name=f'rot_category_2'
        )
        root2.add_child(
            name=f'rot_category_12'
        )
        root2.save()

    def gen_json(self,q_set):
        json_serialize = []
        for node in q_set:
            if node.get_children_count() == 0:
                obj = {
                        "pk": node.pk,
                        "name": node.name,
                        "children": [{ "username":user.username,"email":user.email,"phone":user.phone } for  user in node.users.all()],
                    }

            else:
                obj = {
                    "pk": node.pk,
                    "name": node.name,
                    "children": [{"username": user.username, "email": user.email, "phone": user.phone} for user in
                                 node.users.all()],
                    "category_children": self.gen_json(node.get_children())
                }
            json_serialize.append(obj)
        return json_serialize

    def test_gen_root(self):
        json_serialize = self.gen_json(TreeCategory.get_tree())
        print(json.dumps(json_serialize))

    def tree_move(self,obj):
        type_of, pk = obj['tomove'].split(":")
        tomove = TreeCategory.objects.get(pk=pk)

        type_of ,pk = obj['target'].split(":")
        if type_of == 's':
            target = TreeCategory.objects.get(pk=pk)
            target.parent = tomove
            target.save()
        else:
            target = CustomUser.objects.get(pk=pk)
            tomove.users.add(target)

    def test_move(self):
        obj = {
            "target": "u:1",
            "tomove": "s:3"
        }
        print(TreeCategory.objects.get(pk=3).users.all())
        self.tree_move(obj)
        print(TreeCategory.objects.get(pk=3).users.all())

        obj = {
            "target": "s:3",
            "tomove": "s:1"
        }
        print(TreeCategory.objects.get(pk=3).parent)
        self.tree_move(obj)
        print(TreeCategory.objects.get(pk=3).parent)

    def create_row(self,obj):
        if obj.get('parent') != None:
            """ add sub struct // user"""
            _,root_pk = obj['parent'].split(":")
            root = TreeCategory.objects.get(pk = root_pk)

            if obj['type'] == "s":
                """ add new struct"""
                ins = TreeCategory(name = obj['name'],sib_order = 1)
                root.add_child(instance = ins )
            else:
                """ add new user"""
                obj = CustomUser(
                    username = obj["name"],
                    email= obj["email"],
                    phone= obj["phone"],
                )
                obj.save()
                root.users.add(obj)
        elif obj['type'] == "s":
            """ add root """
            TreeCategory.add_root(
                name = obj['name']
            )
        else:
            raise ZeroDivisionError

    def test_create_children(self):
        """
        {
        'type':'s',
        "name": "name",
        'email':"email",
        'phone':"phone",
        'parent': 's:1'
        }
        :return:
        """
        obj_1 = {
            "type": 'u',
             "name": "name",
             "email": "email",
             "phone": "phone",
             "parent": "s:1"
        }

        obj_2 = {
            "type": 's',
             "name": "name",
             "parent": "s:1"
        }
        obj_3 = {
            "type": 's',
             "name": "name",
             "email": "email",
             "phone": "phone",
        }

        obj_4 = {
            "type": 'u',
             "name": "name",
             "email": "email",
             "phone": "phone",
        }
        self.create_row(obj_1)
        self.create_row(obj_2)
        self.create_row(obj_3)
        try:
            self.create_row(obj_4)
        except ZeroDivisionError:
            pass

    def change_row(self,data):
        type_obj, pk = data['pk'].split(":")
        del data['pk']
        if type_obj == 's':
            obj = TreeCategory.objects.get(pk=pk)
            obj.name = data['name']
            obj.save()
        else:
            obj = CustomUser.objects.get(pk=pk)
            print(obj)
            for attr in data.keys() :setattr(obj,attr,data[attr])
            print(obj)
            obj.save()


    def test_change(self):
        obj_1 = {
            "pk":"s:1",
            "name":"test_data"
        }
        self.change_row(obj_1)
        obj_2 = {
            "pk": "u:1",
            "username": "name",
            "email": "email",
            "phone": "123",
        }
        print(CustomUser.objects.get(pk=1).username)
        self.change_row(obj_2)
        print(CustomUser.objects.get(pk=1).username)
        obj_3 = {
            "pk":"u:1",
            "phone": "123",
        }
        self.change_row(obj_3)
        print("Struct",CustomUser.objects.get(pk=1).phone)

