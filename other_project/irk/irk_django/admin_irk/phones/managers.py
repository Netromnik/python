# -*- coding: UTF-8 -*-
from django.db import models


class Files(models.Manager):
    def get_count(self):
        return self.exclude(file='').count()
        
    count = property(get_count)
    
    
class Section(models.Manager):
    def getTop(self):
        pass
