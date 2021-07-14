# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
from freezegun import freeze_time

from django_dynamic_fixture import G
from django.contrib.contenttypes.models import ContentType

from irk.tests.unit_base import UnitTestBase
from irk.news.tests.unit.material import create_material
from irk.news.management.commands.news_disable_comments import need_disable_comments
from irk.news.models import News
from irk.comments.models import Comment


class CommentsDisableTestCase(UnitTestBase):
    """ Тестирование отключения комментов
    Если новость была добавлена с 09:00 до 17:00, то отключаем каменты через 4 часа после времени написания последнего.
    Либо если ни одного камента не было через 4 часа после времени публикации новости.
    Если новость была добавлена с 17:00 до 09:00, то закрываем каменты не раньше 10 утра следующего дня.
    При отключении каментов они скрываются и выводится заглушка с пояснительным текстом. """

    def setUp(self):
        self.news_ct = ContentType.objects.get_for_model(News)

    def add_comment(self, news, created):
        return G(Comment, content_type=self.news_ct, target_id=news.id, created=created)

    def check_condition(self, news_created_time, last_comment_time, current_time, result):
        news_created_stamp = datetime.datetime.strptime(news_created_time, "%Y-%m-%d %H:%M")
        news = create_material('news', 'news', stamp=news_created_stamp.date(),
                               published_time=news_created_stamp.time(), disable_comments=False)
        if last_comment_time:
            self.add_comment(news, datetime.datetime.strptime(last_comment_time, "%Y-%m-%d %H:%M"))
        with freeze_time(current_time):
            self.assertEqual(need_disable_comments(news), result)

    def test_disable_comments(self):

        # Дата публикации новости | Дата публикации последнего коммента | Текущее время | Результат

        # Тестирование для закрытия комментариев через 4 часа
        # conditions = [
        #     # Новость опубликована c 9:00 по 17:00
        #     ['2017-01-01 9:00', None, '2017-01-01 12:00', False],
        #     ['2017-01-01 9:00', None, '2017-01-01 14:00', True],
        #     ['2017-01-01 9:00', '2017-01-01 12:00', '2017-01-01 14:00', False],
        #     ['2017-01-01 9:00', '2017-01-03 18:00', '2017-01-03 21:00', False],
        #     ['2017-01-01 9:00', '2017-01-03 16:00', '2017-01-03 21:00', True],
        #     ['2017-01-02 9:00', None, '2017-01-01 12:00', False],
        #     # Новость опубликована до 9:00
        #     ['2017-01-01 1:00', None, '2017-01-01 9:30', False],
        #     ['2017-01-01 1:00', None, '2017-01-01 10:00', True],
        #     ['2017-01-01 1:00', '2017-01-01 9:00', '2017-01-01 10:00', False],
        #     ['2017-01-01 1:00', '2017-01-01 9:00', '2017-01-01 14:00', True],
        #     ['2017-01-02 1:00', None, '2017-01-01 12:00', False],
        #     # Новость опубликована после 17:00
        #     ['2017-01-01 18:00', None, '2017-01-01 19:00', False],
        #     ['2017-01-01 18:00', None, '2017-01-01 23:00', False],
        #     ['2017-01-01 18:00', None, '2017-01-02 9:00', False],
        #     ['2017-01-01 18:00', None, '2017-01-02 10:00', True],
        #     ['2017-01-01 18:00', '2017-01-02 8:00', '2017-01-02 10:00', False],
        #     ['2017-01-01 18:00', '2017-01-02 8:00', '2017-01-02 10:00', False],
        #     ['2017-01-02 18:00', None, '2017-01-01 12:00', False],
        # ]

        # Тестирование для закрытия комментариев через  24 часа
        conditions = [
            # Новость опубликована c 9:00 по 17:00
            ['2017-01-01 9:00', None, '2017-01-01 10:00', False],
            ['2017-01-01 9:00', None, '2017-01-02 8:00', False],
            ['2017-01-01 9:00', None, '2017-01-02 10:00', True],
            ['2017-01-01 9:00', '2017-01-01 12:00', '2017-01-02 11:00', False],
            ['2017-01-01 9:00', '2017-01-01 12:00', '2017-01-02 13:00', True],
            # Новость опубликована до 9:00
            ['2017-01-01 1:00', None, '2017-01-01 9:30', False],
            ['2017-01-01 1:00', None, '2017-01-02 0:30', False],
            ['2017-01-01 1:00', None, '2017-01-02 2:00', True],
            ['2017-01-01 1:00', '2017-01-01 22:00', '2017-01-02 21:00', False],
            ['2017-01-01 1:00', '2017-01-01 22:00', '2017-01-02 23:00', True],
            ['2017-01-02 1:00', None, '2017-01-01 12:00', False],
            # Новость опубликована после 17:00
            ['2017-01-01 18:00', None, '2017-01-01 19:00', False],
            ['2017-01-01 18:00', None, '2017-01-02 17:00', False],
            ['2017-01-01 18:00', None, '2017-01-02 19:00', True],
            ['2017-01-01 18:00', '2017-01-02 8:00', '2017-01-02 9:00', False],
            ['2017-01-01 18:00', '2017-01-02 8:00', '2017-01-03 7:00', False],
            ['2017-01-01 18:00', '2017-01-02 8:00', '2017-01-03 9:00', True],
            ['2017-01-02 18:00', None, '2017-01-01 12:00', False],
        ]

        for condition in conditions:
            self.check_condition(*condition)
