# -*- coding: utf-8 -*-

"""Class-based views для новостей"""


class SectionNewsBaseView(object):
    """Mix-in для всех View новостей раздела"""

    # Модель категорий новостей раздела
    category_model = None

    # Название поля у модели новостей раздела, указывающего на модель категорий. Без _id в конце!
    category_model_field = 'section_category'
