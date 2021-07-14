from typing import  Any, Union, Type

from tortoise.models import Model
from tortoise import fields
from pydantic import FilePath, validate_arguments

from ..schems import Photo


class Image(fields.CharField):
    field_type = Photo

    @validate_arguments
    def __init__(self, max_length: int, upload_to: FilePath, **kwargs: Any) -> None:
        self.upload_to = upload_to
        super(Image, self).__init__(max_length, **kwargs)

    def to_db_value(self, value: Photo, instance: "Union[Type[Model], Model]") -> str:
        """
        Load s3 back image
        """
        return super(Photo, self).to_db_value(value.name, instance)

    def to_python_value(self, value: str) -> field_type:
        """
            Load from s3 back
        """
        return Photo(
            name = value,
            file = self.upload_to.name + value
        )


class Fact(Model):
    id = fields.IntField(pk=True)
    number = fields.IntField()
    content = fields.CharField(max_length=200)

    class Meta:
        verbose_name = 'Факт'
        verbose_name_plural = 'Факты'
        ordering = ['number']

    def __str__(self):
        return str(self.number)


class Congratulation(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    contact = fields.CharField(max_length=200)
    position = fields.CharField(max_length=200)
    content = fields.CharField( max_length=200)
    is_visible = fields.BooleanField(default=False, db_index=True)
    photo = Image(upload_to='img/site/irkutsk360/congratulation', blank=True)

    class Meta:
        verbose_name = 'Поздравление'
        verbose_name_plural = 'Поздравления'

    def __str__(self):
        return self.name
