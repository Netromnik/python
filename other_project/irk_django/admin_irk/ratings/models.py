# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save

from irk.ratings.cache import invalidate
from irk.ratings.managers import RatingObjectManager


class RatingObject(models.Model):
    """Объект голосования"""

    content_type = models.ForeignKey(ContentType)
    object_pk = models.PositiveIntegerField()  # TODO rename to object_id
    total_cnt = models.PositiveIntegerField(u'Количество голосов', default=0)
    total_sum = models.IntegerField(u'Сумма голосов', default=0, db_index=True)

    objects = RatingObjectManager()

    class Meta:
        db_table = u'rating_objects'
        verbose_name = u'объект голосования'
        verbose_name_plural = u'объекты голосования'
        unique_together = (('content_type', 'object_pk'),)

    def average(self):
        try:
            return self.total_sum / float(self.total_cnt)
        except ZeroDivisionError:
            return 0


class Rate(models.Model):
    """Голос за объект"""

    obj = models.ForeignKey(RatingObject, related_name='rates')
    user = models.ForeignKey(User)
    ip = models.PositiveIntegerField(blank=True, null=True, default=None)
    user_agent = models.CharField(blank=True, max_length=255, db_index=True, default='')
    value = models.IntegerField()
    created = models.DateTimeField(u'Дата создания', auto_now_add=True, editable=False)

    class Meta:
        db_table = u'rating_values'
        verbose_name = u'голос'
        verbose_name_plural = u'голоса'
        unique_together = (('obj', 'user'),)

    def __unicode__(self):
        return unicode(self.value)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Rate, self).save(*args, **kwargs)

        # Для нового голоса пересчитываем счетчики у объекта голосования
        if is_new:
            RatingObject.objects.filter(pk=self.obj.pk).update(
                total_cnt=models.F('total_cnt') + 1, total_sum=models.F('total_sum') + self.value
            )


post_save.connect(invalidate, sender=Rate)


class RateableModel(models.Model):
    """Примесь для моделий для которым необходим  новый рейтинг (Байес)"""

    rating = models.FloatField(u'Рейтинг', default=0)

    class Meta:
        abstract = True
