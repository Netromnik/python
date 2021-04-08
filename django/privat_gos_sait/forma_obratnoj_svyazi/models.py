from django.db import models

# Create your models here.
class Contact_bd(models.Model):
    name  = models.CharField(max_length=20,null=True,verbose_name="имя")
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=11,null=True,verbose_name="Телефон")
    text  = models.TextField(max_length=200,blank=True,verbose_name="текст")
    select_list=models.TextField(null=True,verbose_name="Список в корзине")
    date  = models.DateTimeField(auto_now=True,verbose_name="Дата")
    class Meta:
        verbose_name="Таблица со списком обратной формы"
        verbose_name_plural="Таблица со списком запросов из  обратной формы"
