from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class BaseHistoryModel(models.Model):
    object = models.Manager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try :
            obj = self.__class__.object.get(pk = self.pk)
        except ObjectDoesNotExist:
            return super(BaseHistoryModel, self).save(force_insert, force_update, using,update_fields)
        dict =self.__dict__
        diff = [ i  for i in obj.__dict__.keys() if i != "_state" and getattr(obj,i) != getattr(self,i) ]
        return super(BaseHistoryModel, self).save(force_insert, force_update, using,
             update_fields=set(diff))

    class Meta:
        abstract = True
