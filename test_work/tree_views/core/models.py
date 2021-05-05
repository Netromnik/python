from django.db import models

from treebeard.al_tree import AL_Node

from django.contrib.auth.models import AbstractUser

class WorkSelect(models.Model):
    name = models.CharField(max_length=12,unique=True,db_index=True)


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=12,verbose_name="Телефон")
    work = models.ForeignKey(WorkSelect,null=True,on_delete=models.SET_NULL)
    name_user_full = models.CharField(max_length=12,verbose_name="Полное имя")

    def get_full_name(self):
        return self.name_user_full

    def get_work(self):
        if (self.work == None):
            work = ''
        else:
            work = self.work.name
        return work
class TreeCategory(AL_Node):
    parent = models.ForeignKey('self',
                               related_name='children_set',
                               null=True,
                               on_delete=models.CASCADE,
                               db_index=True)
    sib_order = models.PositiveIntegerField()
    name =  models.CharField(max_length=120,verbose_name="Названия категории")
    users = models.ManyToManyField(CustomUser,verbose_name="Пользователи")
    is_active = models.BooleanField(verbose_name="Активна",default=True)

    def get_json(self):
        return {
                        "pk":self.pk,
                        "name": self.name,
                        "children": self.users.all(),
                }
    def get_json_parent(self,category):
        return {
                        "pk":self.pk,
                        "name": self.name,
                        "children": self.users.all(),
                        "category_children":category
                }
    def get_children(self):
        """filters is_active"""
        q = super().get_children()
        return q.filter(is_active=True)

    @classmethod
    def get_tree(cls, parent=None):
        """ filters  is_active"""
        q = cls.objects.filter(parent=None)
        return [ node for node in q if node.is_active ]

    def __str__(self):
        return f"{self.pk}:{self.name}"
