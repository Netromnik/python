from django.db import models
from django.shortcuts import reverse

class StreamManeger(models.Manager):
    def tree_create(self,q,view_name):

        sub = self.obj.filter(queue__id=q)
        obj = [{"name": i.description, "url": reverse(view_name, args=[q.pk, i.pk])} for i in sub]
        return obj_list

