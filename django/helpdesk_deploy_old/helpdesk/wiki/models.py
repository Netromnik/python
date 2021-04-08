from django.db import models
from django.contrib.auth import get_user_model
from .manager import WikiNodeManeger
from django.shortcuts import reverse
User = get_user_model()

# Create your models here.
class WikiArticleModel(models.Model):
    """
    title = ,
    slug = ,
    content = ,
    author = ,
    if not root
        level =

    parent
    path
    level
    """

    """ Article """
    title = models.CharField(max_length=120,verbose_name="Заголовок")
    slug = models.SlugField(max_length=140,verbose_name="ЧПУ")
    content = models.CharField(max_length=600,verbose_name="Контент")
    is_publish =models.BooleanField(default=False,verbose_name="Опубликованна ли страница")
    order = models.PositiveIntegerField(verbose_name="Метрика", help_text="От максимума к минимому",default=0)

    """ To logs """
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=False,verbose_name="Автор")
    change_user = models.ForeignKey(
        User,
        models.SET_NULL,
        verbose_name='Последний изменивший',
        blank=True,
        null=True,
        default="",
        related_name="+"
    )
    date_created = models.DateTimeField(auto_now_add=True,verbose_name="Время создания")
    date_update = models.DateTimeField(auto_now=True,verbose_name="Дата обновления")

    """ For Adjacency list """
    delimiter = ":"
    parent = models.ForeignKey("WikiArticleModel",on_delete=models.CASCADE,blank=True,null=True,verbose_name="Родитель")
    path = models.CharField(max_length=120,null=True,blank=True,verbose_name="Путь")
    level = models.PositiveIntegerField(blank=False,db_index=True,verbose_name="Уровень")

    node_manager = WikiNodeManeger()

    def _create_path(self):
        """
        add path
        root : ""
        sub : root.pk
        subsub : root.pk:sub.pk
        :return:
        """
        if self.parent.level == 0:
            return self.parent.pk
        else:
            return "{}{}{}".format(self.parent.path,self.delimiter,self.parent.pk)

    def url(self):
        return reverse("wiki:wiki_page",args=[self.pk,])
    def get_content(self):
        if len(self.content) <1:
            return "{}"
        else:
            return self.content
    def get_children(self):
        return self.wikiarticlemodel_set.filter(level = self.level + 1 , parent = self.pk )
    def get_children_is_publish(self):
        return self.wikiarticlemodel_set.filter(level = self.level + 1 , parent = self.pk, is_publish=True)

    def get_root(self):
        if self.get_parent() == self:
            return self
        else:
            obj = self.get_parent().get_parent()
            return obj

    def get_parent(self):
        if self.level == 0:
            return self
        else:
            return self.parent

    def add_children(self,node):
        """
        ! node not save
        - add perent key
        - add level
        - save model
        - create path
        - save model
        """

        node.parent_id = self.id
        node.level = self.level + 1
        node.path = node._create_path()
        node.save()

    def get_perm(self,user):
        return WikiPermModel.manager_perm.filter(group__in = user.groups.all(),node = self)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "Запись в вики"
        verbose_name_plural = "Записи в вики"
        ordering = ['order']

class WikiPermManeger(models.Manager):
    def get_perm_node(self,node):
        root = node.get_root()
        if self.filter(node_id = root.id).count() > 0:
            return True
        else:
            return False

    def add_perm(self,node,group):
        obj = self.model(node = node,group = group)
        obj.save()

    def dell_all_perm_group(self,group):
        obj = self.filter(group = group)
        obj.delete()

class WikiPermModel(models.Model):
    node  = models.OneToOneField(WikiArticleModel,models.CASCADE, verbose_name="Запись в вики")
    group = models.ForeignKey("base.CustomGroup",models.CASCADE,verbose_name="Группы")
    manager_perm = WikiPermManeger()
    def __str__(self):
        return self.node.title
    class Meta:
        verbose_name = "Разрешение"
        verbose_name_plural = "Разрешения"
