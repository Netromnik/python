from django.db import models
from markdownx.models import MarkdownxField
class categor_post(models.Model):
    categor=models.CharField(max_length=200,primary_key=True)
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Тип постов"
        verbose_name_plural="Типы постов"

class Post(models.Model):
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,verbose_name="Автор поста"
    )
    title = models.CharField(max_length=200,verbose_name="Заголовок поста")
    image_title = models.ImageField(upload_to='news/post/image/title',verbose_name="Изображения в шапки поста")
    categor= models.ForeignKey(
        'categor_post',
        on_delete=models.CASCADE,verbose_name="Котегория поста"
    )
    introduese=models.TextField(max_length=300,verbose_name="Анотация")

    content=MarkdownxField(max_length=1200,verbose_name="Главный текст")
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-date']
        verbose_name = "Список постов"
        verbose_name_plural="Cписок постов"

    def __str__(self):
        return self.title

    #
    # GENDER_CHOICES = [
    #     (MAN, 'Мужской'),
    #     (FEMALE, 'Женский'),
    # ]
    # gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MAN, verbose_name="Пол",)
    #