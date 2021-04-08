from django.db import models
from mdeditor.fields import MDTextField
#
# class categoy(models.Model):
#     name=models.CharField(max_length=200,primary_key=True)
#     slug=models.SlugField(max_length=200,unique=True)
#
#     class Meta:
#         ordering=['name']
#         verbose_name = "Категория"
#         verbose_name_plural = "Категории"
#
#     def __str__(self):
#         return self.name

# Create your models here.
class pattern_for(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField()
    text =MDTextField()    
    categor_choise=(
        ("for_biznes","для бизнеса"),
        ("for_gos","для государства")
    )
    categoy=models.CharField(choices=categor_choise,default=categor_choise[0],max_length=30)
    image_title=models.ImageField(upload_to='pattern',blank=True)
    image_priview=models.ImageField(upload_to='pattern',blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name="Запис в категориях"
        verbose_name_plural="Записи в категориях"

    def get_image(self):
        a= 'media/'+str(self.image)+".png"
        return a

    def __str__(self):
        return "{} {} ".format(self.name,self.categoy)

    def get_absolute_url(self):
        return "/art/" + str(self.categoy)+ "/" + str(self.slug)+"/"
