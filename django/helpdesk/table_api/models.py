from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
User = get_user_model()


class SettingsTable(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    table_id = models.CharField(max_length=60)
    json_dump = models.TextField(verbose_name="Данные для модели",blank=True,null=True)
    object = models.Manager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not SettingsTable.object.filter(user = self.user,table_id =self.table_id).count() <2:
            SettingsTable.object.filter(user=self.user, table_id=self.table_id).delete()
        super().save()

    def __str__(self):
        return self.table_id

class AnaliticTable(models.Model):
    groups = models.ManyToManyField(Group)
    date_create = models.DateTimeField(verbose_name="время создания",auto_now_add=True,db_index=True)
    state = models.CharField(max_length=35,verbose_name="Состояния заявки")
    object = models.Manager()
