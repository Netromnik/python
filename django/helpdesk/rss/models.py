from django.db import models
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class RssId:
    seed = models.IntegerField(primary_key=True,verbose_name="uniq sid")
    content = models.ForeignKey(ContentType,on_delete=models.CASCADE,verbose_name="meta deta")
    id_row =models.IntegerField()
