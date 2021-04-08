from django.db import models
from mdeditor.fields import MDTextField
# Create your models here.

class name_cat(models.Model):
    name = models.CharField(max_length=30,primary_key=True)
    slug = models.SlugField()
    image = models.ImageField(upload_to='prod/catalog/name', blank=True)

    class Meta:
        verbose_name="Имя категории"
        verbose_name_plural="Имя категорий"

    def __str__(self):
        return "{}  ".format(self.name)

class items_cat(models.Model):
    name = models.CharField(max_length=30,primary_key=True)
    slug = models.SlugField()
    text =MDTextField()
    image=models.ImageField(upload_to='prod/catalog/',blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    categoy=models.ForeignKey(name_cat,on_delete=models.CASCADE)

    class Meta:
        verbose_name="Каталог продукции"
        verbose_name_plural="Каталог продаваемой продукции"

    def get_image(self):
        return  str( 'for_gos/'+self.image+".png")

    def __str__(self):
        return "{} {} ".format(self.name,self.categoy)

    def get_absolute_url(self):
        return "/mag/" + str(self.categoy)+ "/" + str(self.slug)+"/"
