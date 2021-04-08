from django.db import models


class CustomSlugField(models.CharField):
    def create