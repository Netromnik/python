# -*- coding: utf-8 -*-

from django.db import models


# TODO: перенести в приложение statistic
class MaterialScrollStatistic(models.Model):
    """Статистика доскролла для материалов"""

    material = models.OneToOneField('news.BaseMaterial', verbose_name=u'материал', related_name='scroll_statistic')
    # показатели
    point_1 = models.PositiveIntegerField(u'открыли', default=0)
    point_2 = models.PositiveIntegerField(u'начали читать', default=0)
    point_3 = models.PositiveIntegerField(u'доскролили до середины', default=0)
    point_4 = models.PositiveIntegerField(u'доскролили до лайков', default=0)
    point_5 = models.PositiveIntegerField(u'читали комментарии', default=0)

    start_read = models.PositiveIntegerField(u'начали читать текст', default=0)
    read_time = models.PositiveIntegerField(u'время чтения (сек)', default=0)
