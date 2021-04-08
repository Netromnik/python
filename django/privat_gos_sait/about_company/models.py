from django.db import models
from markdownx.models import MarkdownxField
from os import listdir
# Create your models here.
from django.db import models

# Create your models here.

def choices_dir_file():
    directory = '/sait/privat_gos_sait/media/about_company/list_others_pages'
    dict={("def","noimage.png")}
    for i in listdir(directory):
        dict.add(("media/about_company/list_others_pages/"+str(i),str(i)))
    return tuple(dict)

class about_company(models.Model):
    def creat(selfs):
        pass

    def __str__(self):
        return '{}'.format(self.title)

class item_block(models.Model):
    item1=  models.CharField(max_length=40)
    item2 = models.CharField(max_length=40)
    item3 = models.CharField(max_length=40)
    item4 = models.CharField(max_length=40)



class list_menu(models.Model):
    image_choise=choices_dir_file()
    title = models.CharField(max_length=40,verbose_name="Заголовок")
    content = MarkdownxField(max_length=1200,blank=True,verbose_name="текст")
    image = models.CharField(max_length=80,choices=image_choise,default=image_choise[0],blank=True,verbose_name="изображения")
    slug = models.SlugField(verbose_name="уникальная ссылка")
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name="Страница находящяяся на главном странице"
        verbose_name_plural="Страницы на главной странице с имформацией о компании"

    def get_url(self):
        return "list/{}".format(self.slug)
    def __str__(self):
        return self.title
