# -*- coding: utf-8 -*-

from django.db.models import Avg

from irk.ratings.models import RatingObject, Rate
from irk.ratings import settings

from irk.utils.tasks.helpers import task


@task
def bayes_rating_count(obj, rating_object):
    """ Пересчт рейтнга для объекта"""
    model_total = RatingObject.objects.filter(content_type=rating_object.content_type).aggregate(Avg('total_sum'),
                                                                                                 Avg('total_cnt'))

    # Среднее для всех объектов
    all_avarage_rating = model_total['total_sum__avg'] / model_total['total_cnt__avg']

    # Минимальное число голосов для участия в рейтинге
    minimum_votes = settings.BAYES_MINIMUM_VOTES

    rate_count = Rate.objects.filter(obj=rating_object).count()

    if rate_count >= minimum_votes:
        avarage_rating = rating_object.total_sum / rating_object.total_cnt

        rating = (rate_count * avarage_rating +
                  minimum_votes * all_avarage_rating) / (minimum_votes + rate_count)

        obj.rating = float(rating)
        obj.save()
