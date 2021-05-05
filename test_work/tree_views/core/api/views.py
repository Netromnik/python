import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render

from core.models import TreeCategory, CustomUser,WorkSelect


# Create your views here.
def vue_app(request):
    return render(request, 'index.html')

def selected_api(request):
    data = [ i.name for i in WorkSelect.objects.all() if len(i.name) !=0]
    print(data)
    return JsonResponse(data,safe=False)


class ApiCrud(View):
    # http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def gen_json(self, q_set):
        json_serialize = []
        for node in q_set:
            obj = {
                "pk": f"s:{node.pk}",
                "fields": {"name": node.name},
                "type_obj": 'struct',
                "children": [
                    {"pk": f"u:{user.pk}", "type_obj": 'user',
                     "fields": {"fullname": user.get_full_name(), "email": user.email,
                                "phone": user.phone, 'work': user.get_work()}} for user in
                    node.users.all().filter(is_active=True)],
            }

            if node.get_children_count() != 0:
                obj['tree_children'] = self.gen_json(node.get_children())
            json_serialize.append(obj)
        return json_serialize

    def get(self, *args, **kwargs):
        """ Данный метод нужен для получения дерева"""
        json_serialize = self.gen_json(TreeCategory.get_tree())
        return JsonResponse(json_serialize, safe=False)

    def tree_dell(self,obj):
        type_of, pk = obj['target'].split(":")
        if type_of == 's':
            target = TreeCategory.objects.get(pk=pk)
            target.is_active = False
            target.save()
        else:
            target = CustomUser.objects.get(pk=pk)
            target.is_active = False
            target.save()

    def tree_move(self, obj):
        type_of, pk = obj['tomove'].split(":")
        if type_of == 'u':
            user = CustomUser.objects.get(pk=pk)
            tomove = user.treecategory_set.all()[0]
        else:
            tomove = TreeCategory.objects.get(pk=pk)

        type_of, pk = obj['target'].split(":")
        if type_of == 's':
            target = TreeCategory.objects.get(pk=pk)
            if hasattr(target.parent,'pk'): target_pk = target.parent.pk
            else : target_pk = None
            if target_pk != tomove.pk or target_pk == None:
                target.parent = tomove
                target.save()
        else:
            target = CustomUser.objects.get(pk=pk)
            el = target.treecategory_set.all()[0]
            el.users.remove(target)
            tomove.users.add(target)

    def post(self, *args, **kwargs):
        """ Данный метод нужен для переноса в дерева"""
        """
    {
      target: s:1,
      tomove: u:2
    }
        {
      target: s:1,
      tomove: u:2,
      delete:true,
    }

      """
        js = json.loads(self.request.body)
        try:
            if js.get('dalete'):
                self.tree_dell(js)
            else:
                self.tree_move(js)
        except ObjectDoesNotExist:
            return JsonResponse("404", safe=False)
        return JsonResponse("301", safe=False)

    def create_row(self, obj):
        if obj.get('parent') != None:
            """ add sub struct // user"""
            _, root_pk = obj['parent'].split(":")
            root = TreeCategory.objects.get(pk=root_pk)

            if obj['type'] == "s":
                """ add new struct"""
                ins = TreeCategory(name=obj['name'], sib_order=1,is_active=True)
                root.add_child(instance=ins)
                user  = CustomUser(username = f"s{ins.pk}",is_active=True)
                user.save()
                ins.users.add(
                    user
                )
            else:
                """ add new user"""

                obj ,create = CustomUser.objects.get_or_create(username=obj["username"])
                obj.is_active = True
                obj.save()
                root.users.add(obj)
        elif obj['type'] == "s":
            """ add root """
            ins = TreeCategory(name=obj['name'])
            TreeCategory.add_root(
               instance=ins
            )
            user = CustomUser(username=f"s{ins.pk}", is_active=True)
            user.save()
            ins.users.add(
                user
            )
        else:
            raise ObjectDoesNotExist

    def put(self, *args, **kwargs):
        """ Данный метод нужен для создания новых нод в дереве"""
        js = json.loads(self.request.body)
        try:
            self.create_row(js)
        except ObjectDoesNotExist:
            return JsonResponse("400", safe=False)
        except IntegrityError:
            return JsonResponse("400", safe=False)
        return JsonResponse("201", safe=False)

    def change_row(self, data):
        type_obj, pk = data['pk'].split(":")
        del data['pk']
        fields = data['fields']
        if type_obj == 's':
            obj = TreeCategory.objects.get(pk=pk)
            obj.name = fields['name']
            obj.save()
        else:
            obj = CustomUser.objects.get(pk=pk)
            obj.name_user_full = fields['fullname']
            obj.email = fields['email']
            obj.phone = fields['phone']
            obj.work, _ = WorkSelect.objects.get_or_create(
                name = fields['work']
            )
            obj.save()

    def patch(self, *args, **kwargs):
        """ Данный метод нужен для измененения дерева"""

        js = json.loads(self.request.body)
        try:
            self.change_row(js)
        except ObjectDoesNotExist:
            return JsonResponse("400", safe=False)
        return JsonResponse("201", safe=False)
