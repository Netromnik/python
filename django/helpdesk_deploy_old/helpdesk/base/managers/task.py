from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from base.models_i.chat import ChatModel


class StateTaskManager(models.Manager):
    def get_task(self,id,stream,user):
        task =self.get(pk = id)
        if task.stream.pk != stream['id'] and stream['id'] !=0 :
            raise ValidationError
        task.asignet_to = user
        task.status = task.STATUS[1][0]
        task.save()
        return task

    def chenge_status(self,task,user,status):
        if task.status == status:
            return
        if user == task.asignet_to or user == task.autors or user.is_superuser == True :
            task.status = status
            task.chenge_user = user
            task.save()

class DetailTaskManager(models.Manager):
    def get_task_form(self,user,task):
        # autor asignet None
        asignet_to = task.asignet_to
        autor = task.autors
        if user == autor:
            return self.create_form("autor")
        if user == asignet_to:
            return self.create_form("asignet")



    def create_form(self,choise):
        # CHOICES = (('Option 2', 'Option 2'), ('Option 1', 'Option 1'),)
        if choise == "autor":
            CHOICES = (("O", "Открыта"), ("C", "Закрыто"))
        elif choise == "asignet":
            CHOICES = (("O", "Открыта"), ("S", "Решено"),)
        else:
            return None

        class TicketForm(forms.Form):
            mesenge = forms.CharField(widget=forms.Textarea, label="Сообщения")
            status = forms.ChoiceField(choices=CHOICES, label="Статус")


        return TicketForm
    def create_row_insert(self,title,body,class_css="inline-block"):
        # obj = {"title": "Content", "class": "inline-block", "body": "test fasf asf ", }
        obj = {}
        obj["title"] = title
        obj["class"] = class_css
        obj["body"] = body
        return obj

    def get_task(self,task):
        # obj = {
        #     "title": "1212. Test Task [Open]",
        #     "rows" : [
        #         {"title":"Content","class": "inline-block","body": "test fasf asf ",},
        #         {"title":"Content2","class": "inline-block","body": "test fasf asf ",},
        #         {"title":"Content3","class": "inline-block","body": "test fasf asf ",},
        #         {"title":"Content3","class": "char-block","body": "test fasf asfasd as dd sfsdf  ",},
        #         {"title":"Content3","class": "file-fields-block","body": "test fasf asfasd as dd sfsdf  ","is_file":True,
        #          "files":[
        #              {"name":"f1","url":"#"},
        #              {"name":"f2","url":"#"},
        #              {"name":"f3","url":"#"},
        #          ]},
        #     ]
        # }
        obj = {}
        obj['title'] = "[#{}] {} [{}]".format(task.pk,task.title,task.get_status())

        inline_list = [
            "stream",
            "autors",
            "created_at",
            "updated_at",
            "date_due",
        ]
        if task.asignet_to !=None:
            inline_list.insert(2,"asignet_to")
        char_block_list = [
            "description",
        ]
        if task.file != None:
            file =  {"title":getattr(task.__class__,"file",).field.verbose_name.capitalize(),"class": "file-fields-block","body": "","is_file":True,
                 "files":[
                     {"name":task.file,"url":task.file.url()},
                     # {"name":"f2","url":"#"},
                     # {"name":"f3","url":"#"},
                 ]}
        else:
            file = {}

        inline_row_list = [ self.create_row_insert(title=getattr(task.__class__,i,).field.verbose_name.capitalize(),body=getattr(task,i)) for i in inline_list]
        char_row_list = [ self.create_row_insert(title=getattr(task.__class__,i,).field.verbose_name.capitalize(),body=getattr(task,i),class_css="char-block") for i in char_block_list]
        obj["rows"] = inline_row_list + char_row_list + [file]
        return obj


    def get_chat(self,task,user):
        obj_list = []
        asignet_to = task.asignet_to
        autor = task.autors
        if user != autor and asignet_to !=user or asignet_to == None:
            return {}
        chats = ChatModel.obj.filter(task=task)
        for messenge in chats:
            obj = {}
            if messenge.user  == autor:
                obj["color"] ="red"
            elif messenge.user == asignet_to:
                obj["color"] = "blue"
            obj["user"] = messenge.user.__str__()
            obj["body"] = messenge.mesenge
            obj["date"] = messenge.updated_at
            obj_list.append(obj)
        return {"is_chat":True,"obj":obj_list,}


class CustomManegerTaskSelf(models.Manager):
    ## return stat +!
    ## return is_avtor Task +
    ## return is use for stream
    ## return is use for asignet

    def all_task_for_user(self,user):
        task_q_asignet_to = self.filter(asignet_to = user)
        task_q_autors = self.filter(autors = user)
        task_q_summ = self.none()
        task_q_summ |= task_q_autors | task_q_asignet_to
        return task_q_summ

    def all_chat_for_user(self,user):
        task = self.all_task_for_user(user)
        chat_id = ChatModel.obj.filter(task__in =task)
        return chat_id

    def _stat(self,name,all,list):
        obj = {
            "title":name,
            "all":all,
                }
        obj["stats"] = list
        return obj
    def _stats_d(self,f,ques):
        count = ques.count()
        f["all"] = count
        f_valid = []
        for stat in f["filter_l"]:
            c = ques.filter(status=stat["status"]).count()
            name = stat["name"]
            f_valid.append({
                "name":name,
                "data":c
            })
        del f["filter_l"]
        f["stats"] = f_valid
        return f

    def  stats(self,user):
        data = []
        task_q_asignet_to = self.filter(autors=user)
        f = {"filter_l": [
            {"name": "Ожидает",
             "status": "W"
             },
            {"name": "Ваполняется",
             "status": "O"
             },
            {"name": "Закрыто",
             "status": "C"
             },
            ],
            "title": "Созданные вами заявки",
            "all": 12,
        }
        data.append( self._stats_d(f,task_q_asignet_to))

        task_q_asignet_to = self.filter(asignet_to=user)
        f = {"filter_l": [
            {"name": "Ваполняется",
             "status": "O"
             },
            {"name": "Решено",
             "status": "S"
             },

            {"name": "Закрыто",
             "status": "C"
             },
            ],
            "title": "Выполняемые вами заявки",
            "all": 12,
        }
        data.append( self._stats_d(f,task_q_asignet_to))
        return data

    def is_avtor(self,user):
        return self.filter(autors=user)


