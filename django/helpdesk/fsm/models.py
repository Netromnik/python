from django.db import models
from django_fsm import FSMField, transition
from django.contrib.auth.models import  Group
from mptt.models import MPTTModel, TreeForeignKey
from notifications.signals import notify
from .manager.task import CustomManegerTaskStatistic
from django.contrib.auth import get_user_model
from .manager.queue import SupportQManager
from django.core.exceptions import ObjectDoesNotExist
User = get_user_model()
from table_api.models import AnaliticTable

## save file
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
import os

# Create your models here.
STATES_list = ('Открыта', 'Ваполняется', 'Решена', 'Переоткрыта', 'Ошибка', 'Закрыта')
STATES = list(zip(STATES_list, STATES_list))

the_importance_list = ( 'Низкая','Обычная', 'Высокая', 'Горит')
the_importance = [
    ("warm",'Горит'),
    ("high",'Высокая'),
    ('common','Обычная'),
    ('low','Низкая')
                  ]


class Queue(MPTTModel):
    """
    Основная очеред заявок
    """
    title = models.CharField(max_length=100, null=False, unique=True)
    gr = models.ManyToManyField(Group ,
        verbose_name=_('groups'),
        blank=True,
        related_name="queue_set",
        related_query_name="queue",
)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    support_manager = SupportQManager()

    def url(self):
        return "/{}/{}".format(self.pk,0)

    def get_sub_url(self):
        titles = []
        pr = self
        while pr:
            titles.append(str(pr.pk))
            pr = pr.parent
        return "/" + "/".join(titles[::-1])

    def __str__(self):
        return self.title

    class MPTTMeta:
        order_insertion_by = ['title']

def validate_file(f):
    file_size = f.file.size

    if file_size > int(settings.MAX_UPLOAD_SIZE):
        raise ValidationError("Max size of file is {} MB".format(settings.MAX_UPLOAD_SIZE // 1024 // 1024))

class Task(models.Model):
    """
    Заявки пользователей
    """

    """ Meta date task """
    title = models.CharField(max_length=200, null=False, blank=False, db_index=True, verbose_name="Заголовок заявки")
    description = models.TextField(verbose_name="Описания заявки")
    state = FSMField(default=STATES[0][0], choices=STATES, verbose_name="Состояния заявки")
    queue = models.ForeignKey(Queue, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Зависит от")

    file = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name="Файл", blank=True, null=True)

    """ service information """
    raiting = models.IntegerField(verbose_name="Рейтинг",default=-1)
    the_importance = models.CharField(verbose_name="Уровень важности",choices=the_importance,default=the_importance[1][0],max_length=26)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Создатель",
                              related_name="owner")
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Ответственный", related_name="resp")
    data_create = models.DateTimeField(auto_now=True, blank=False, verbose_name="Время создания")
    data_update = models.DateTimeField(auto_now_add=True, blank=False, verbose_name="Время обновления")
    object = models.Manager()
    statistic_data_manager = CustomManegerTaskStatistic()

    ##########################################################################################
    def __str__(self):
        return "Заявка {} ".format(self.pk)

    def upload_file(self,file):
        # file = File.obj.create(document=file)
        self.file =file
        self.save()

    def file_name(self):
        return os.path.basename(self.file.name)

    def file_url(self):
        return self.file.url
    def file_size(self):
        return "{0:.3f} MB".format(self.file.size / 1024 / 1024)
    def url(self):
        return "/ticket/{}".format(self.pk)
    def url_up(self):
        return "/ticket/api/{}/up/".format(self.pk)
    def url_sessefull(self):
        return "/ticket/api/{}/ok/".format(self.pk)
    def url_close(self):
        return "/ticket/api/{}/close/".format(self.pk)
    def url_re_open(self):
        return "/ticket/api/{}/re_open/".format(self.pk)

    class Meta:
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')
    ##########################################################################################
    def is_owner(self, user: User) -> bool:
        if self.owner == user:
            return True
        else:
            return False

    def is_responsible(self, user: User) -> bool:
        if self.responsible == user:
            return True
        else:
            return False

    def get_role(self, user: User) -> str:
        if self.is_owner(user):
            return "owner"
        elif self.is_responsible(user):
            return "responsible"

    def __save_analitic(self,state):
        q_root = self.queue.get_root()
        r = AnaliticTable.object.create(
            state = state,
                      )
        r.groups.set(q_root.gr.all())

    #######################################################################################
    @transition(field=state, source='*', target='Открыта', on_error='Ошибка')
    def start(self):
        q_root = self.queue.get_root()
        for gr in q_root.gr.all():
            notify.send(self,recipient = gr,verb='была созданна')
        self.__save_analitic('Открыта')

    @transition(field=state, source=['Открыта',"Переоткрыта"], target='Ваполняется', on_error='Ошибка')
    def progress(self):
        notify.send(self,recipient = self.owner,verb='была принята в работу')
        self.__save_analitic('Ваполняется')


    @transition(field=state, source='Ваполняется', target='Решена', on_error='Ошибка')
    def resolve(self):
        notify.send(self,recipient = self.owner,verb='была решена')
        self.__save_analitic('Решена')

    @transition(field=state, source='Решена', target='Закрыта', on_error='Ошибка')
    def close(self):
        notify.send(self, recipient=self.responsible, verb='была закрыта')
        self.__save_analitic('Закрыта')

    @transition(field=state, source='*', target='Переоткрыта', on_error='Ошибка')
    def re_resolve(self):
        notify.send(self, recipient=self.owner, verb='была переоткрыта')
        notify.send(self, recipient=self.responsible, verb='была переоткрыта')
        self.__save_analitic('Переоткрыта')


    @transition(field=state, source="*", target='Ошибка')
    def err(self):
        notify.send(self, recipient=self.owner, verb='ошибка')
        notify.send(self, recipient=self.responsible, verb='ошибка ')
        self.__save_analitic('Ошибка')


def is_sub_page(id_r:int,id_node:int):
    """ Check is node """
    queue = Queue.objects.get(pk=id_r)
    sub_q = Queue.objects.get(pk=id_node)
    if not sub_q.parent == queue:
        raise ObjectDoesNotExist
    return True
