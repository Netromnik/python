# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property

from irk.gallery.fields import ManyToGallerysField
from irk.news import models as news_models
from irk.news.managers import BaseMaterialManager, LongreadMaterialManager, MaterialManager, MagazineMaterialManager
from irk.news.models import material_register_signals
from irk.obed.search import EstablishmentSearch
from irk.phones.models import SectionFirm, Firms as Firm, Sections
from irk.polls import models as polls_models
from irk.testing import models as testing_models
from irk.utils.fields.file import FileRemovableField, ImageRemovableField
from irk.utils.files import generate_file_name


def type_upload_to(obj, filename):
    return "img/site/obed/%s" % generate_file_name(None, filename)


class Type(models.Model):
    """ Тип кухни """

    name = models.CharField(max_length=255, verbose_name=u'Название')
    image = ImageRemovableField(verbose_name=u'Изображение', upload_to=type_upload_to, blank=True)
    position = models.PositiveIntegerField(verbose_name=u'Позиция', default=0)
    firm_count = models.PositiveIntegerField(null=True, editable=False)

    class Meta:
        verbose_name = u'тип'
        verbose_name_plural = u'типы'
        ordering = ('position',)

    def __unicode__(self):
        return self.name

    def recalculate_firms_count(self, exclude=()):
        self.firm_count = self.establishment_set.filter(is_hidden=False, visible=True).exclude(pk__in=exclude).count()
        self.save()


class BarofestManager(models.Manager):
    """
    Выборка участников барофеста 2018 через Establishment.barofest_participants
    """
    def get_queryset(self):
        return super(BarofestManager, self).get_queryset().filter(establishment_barofest__isnull=False)


class Okrug(models.Model):
    """Округа Иркутска"""

    name = models.CharField(u'Название', max_length=100)

    class Meta:
        verbose_name = u'округ'
        verbose_name_plural = u'округа'

    def __unicode__(self):
        return self.name


class Establishment(SectionFirm):
    """ Ресторан/кафе etc. """

    BILL_0_500 = 1
    BILL_500_1000 = 2
    BILL_1000_1500 = 3
    BILL_1500_INF = 4
    BILL_CHOICES = (
        (BILL_0_500, u'до 500 р.'),
        (BILL_500_1000, u'от 500 до 1000 р.'),
        (BILL_1000_1500, u'от 1000 до 1500 р.'),
        (BILL_1500_INF, u'больше 1500 р.'),
    )

    main_section = models.ForeignKey(Sections, verbose_name=u'Основная рубрика')
    obed_id = models.IntegerField(verbose_name=u'ID-заведение с obed.irk.ru', null=True, blank=True, )  # TODO не используется
    old_establishment_id = models.IntegerField(verbose_name=u'ID-заведений до рефакторинга', null=True, blank=True, )  # TODO не используется
    contacts = models.CharField(u'Контакты администрации', max_length=1000, null=True)

    wifi = models.BooleanField(verbose_name=u'Wi-Fi', blank=True, default=False, db_index=True)
    dancing = models.BooleanField(verbose_name=u'Танцпол', blank=True, default=False, db_index=True)
    karaoke = models.BooleanField(verbose_name=u'Караоке', blank=True, default=False, db_index=True)
    children_room = models.BooleanField(verbose_name=u'Детская комната', blank=True, default=False, db_index=True)
    terrace = models.BooleanField(verbose_name=u'Летняя веранда', blank=True, default=False, db_index=True)
    catering = models.BooleanField(verbose_name=u'Выездное обслуживание', blank=True, default=False, db_index=True)
    business_lunch = models.BooleanField(verbose_name=u'Бизнес-ланч', blank=True, default=False, db_index=True)
    business_lunch_price = models.PositiveIntegerField(u'Стоимость бизнес-ланча', null=True, blank=True, db_index=True)
    business_lunch_time = models.CharField(u'Время бизнес-ланча', max_length=30, blank=True)
    cooking_class = models.BooleanField(verbose_name=u'Кулинарные мастер-классы', blank=True, default=False, db_index=True)
    breakfast = models.BooleanField(verbose_name=u'Завтрак', blank=True, default=False, db_index=True)
    children_menu = models.BooleanField(verbose_name=u'Детское меню', blank=True, default=False, db_index=True)
    cashless = models.BooleanField(verbose_name=u'Безнал', blank=True, default=True, db_index=True)
    live_music = models.BooleanField(verbose_name=u'Живая музыка', blank=True, default=False, db_index=True)
    entertainment = models.BooleanField(verbose_name=u'Развлекательная программа', blank=True, default=False, db_index=True)
    banquet_hall = models.BooleanField(verbose_name=u'Банкетный зал', blank=True, default=False, db_index=True)

    parking = models.CharField(verbose_name=u'Парковка', max_length=255, null=True, blank=True)
    facecontrol = models.CharField(verbose_name=u'Вход', max_length=255, null=True, blank=True)

    types = models.ManyToManyField(Type, verbose_name=u'Типы')
    bill = models.PositiveIntegerField(verbose_name=u'Средний чек', choices=BILL_CHOICES, null=True, db_index=True)

    virtual_tour = models.CharField(max_length=255, verbose_name=u'Виртуальный тур', null=True, blank=True)

    card_image = ImageRemovableField(verbose_name=u'Фото для карточки', upload_to='img/site/obed/establishment/',
                                  null=True, blank=True, help_text=u'Размер: 298×140 пикселей')

    # Новогодние корпоративы
    corporative = models.BooleanField(u'Выводить в списке корпоратива', default=False, db_index=True)
    corporative_guest = models.IntegerField(u'Количество гостей', null=True, blank=True)
    corporative_price = models.IntegerField(u'Цена за человека', null=True, blank=True)
    corporative_description = models.TextField(u'Описание', null=True, blank=True)
    corporative_image = ImageRemovableField(verbose_name=u'Фото', upload_to='img/site/obed/corporative', null=True, blank=True)
    # TODO удалить после переноса изображений в галерею

    # Барофест
    barofest_description = models.TextField(u'Описание', default='', blank=True)

    # Летние веранды
    summer_terrace = models.BooleanField(u'Выводить в списке летних веранд', default=False, db_index=True)
    summer_terrace_description = models.TextField(u'Описание для летней веранды', default='', blank=True)

    # Доставка
    delivery = models.BooleanField(u'Выводить в списке доставок', default=False, db_index=True)
    delivery_description = models.TextField(u'Описание для доставок', default='', blank=True)
    delivery_price_free = models.IntegerField(u'Бесплатная доставка от', null=True, blank=True)
    delivery_districts = models.ManyToManyField(Okrug, verbose_name=u'Округ', blank=True)

    is_new = models.BooleanField(u'Новое', default=False, db_index=True)
    last_review = models.ForeignKey('Review', verbose_name=u'Последняя рецензия', null=True, blank=True,
                                    related_name='+', editable=False)

    # Для гастрономической карты
    point = models.CharField(u'Координата текстом', default='', blank=True, max_length=255,
                             help_text=u'Пример: 52.276333,104.336461')
    type_name = models.CharField(u'Название типа заведения', default='', blank=True, max_length=255,
                                 help_text=u'Пример: Ресторан')
    type_name_en = models.CharField(u'Название типа заведения на английском', default='', blank=True, max_length=255,
                                    help_text=u'Пример: Restaurant')
    name_en = models.CharField(u'Английское название', max_length=255, default='', blank=True)
    address_name_en = models.CharField(u'Английское название адреса', max_length=255, default='', blank=True)

    objects = models.Manager()
    barofest_participants = BarofestManager()

    search = EstablishmentSearch()

    class Meta:
        verbose_name = u'заведение'
        verbose_name_plural = u'заведения'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('obed:establishment_read', kwargs={'section_slug': self.main_section.slug,
                                                                'firm_id': self.pk})

    def barofest(self):
        if hasattr(self, 'establishment_barofest'):
            return self.establishment_barofest
        return None

    @cached_property
    def award(self):
        """
        Награда для заведения

        Отображается последняя полученная
        """

        return self.award_set.order_by('created').last()

    @cached_property
    def awards(self):
        """Все награды заведения в убывающем хронологическом порядке"""

        return self.award_set.order_by('-created')

    def get_delivery_districts(self):
        return list(item.id for item in self.delivery_districts.all())

    def update_last_review(self, review):
        """
        Обновить связь на последний обзор для заведения
        """

        # Для скрытого обзора или обзора не привязанного к заведнию, ничего не делаем
        if review.is_hidden or not review.establishment:
            return

        # Обзор другого заведения тоже пропускаем
        if review.establishment != self:
            return

        need_update = False
        if not self.last_review:
            need_update = True
        elif self.last_review and self.last_review.id != review.id:
            # привязываем более свежий обзор
            review = max([review, self.last_review], key=lambda m: m.stamp)
            need_update = True

        if need_update:
            self.last_review = review
            self.save()


class Menu(models.Model):
    """Меню заведения"""

    establishment = models.OneToOneField(Establishment, related_name='establishment_menu', verbose_name=u'Заведение')

    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'меню заведения'
        verbose_name_plural = u'меню заведения'

    def __unicode__(self):
        return self.establishment.name


class SummerTerrace(models.Model):
    """Летняя веранда"""

    establishment = models.OneToOneField(Establishment, related_name='establishment_summer_terrace',
                                         verbose_name=u'Заведение')

    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'летняя веранда'
        verbose_name_plural = u'летние веранды'

    def __unicode__(self):
        return self.establishment.name


class Delivery(models.Model):
    """Доставка"""

    establishment = models.OneToOneField(Establishment, related_name='establishment_delivery',
                                         verbose_name=u'Заведение')

    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'доставка'
        verbose_name_plural = u'доставки'

    def __unicode__(self):
        return self.establishment.name


class Corporative(models.Model):
    """Корпоратив"""

    establishment = models.OneToOneField(Establishment, related_name='establishment_corporative',
                                         verbose_name=u'Заведение')

    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'корпоратив'
        verbose_name_plural = u'корпоративы'

    def __unicode__(self):
        return self.establishment.name


class BarofestParticipant(models.Model):
    """
    Заведение-участник Байкальского гастрономического фестиваля 1.04.2018
    """

    establishment = models.OneToOneField(Establishment, related_name='establishment_barofest',
                                         verbose_name=u'Заведение')

    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'участник БГФ 2018'
        verbose_name_plural = u'участники барофеста 2018'

    def __unicode__(self):
        return self.establishment.name


class ArticleCategory(models.Model):
    """Категории статей раздела"""

    title = models.CharField(u'Название', max_length=255)
    slug = models.SlugField()
    position = models.PositiveIntegerField(u'Позиция', default=0)

    class Meta:
        db_table = 'obed_article_categories'
        verbose_name = u'категория статей'
        verbose_name_plural = u'категории статей'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        raise NotImplementedError()


@material_register_signals
class Article(news_models.Article):
    """Статьи раздела"""

    article_ptr = models.OneToOneField('news.Article', parent_link=True, related_name='obed_article')
    section_category = models.ForeignKey(ArticleCategory, verbose_name=u'Категория раздела')
    mentions = models.ManyToManyField(Establishment, related_name='mentions', blank=True, verbose_name=u'Упоминания')
    main_announcement = models.BooleanField(u'Анонсировать на главной', db_index=True, default=True)

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    class Meta(news_models.Article.Meta):
        db_table = 'obed_articles'
        verbose_name = u'статья'
        verbose_name_plural = u'статьи'

    def is_review(self):
        """ Является ли статья рецензией """
        try:
            return True if self.obed_review else False
        except ObjectDoesNotExist:
            return False

    def get_social_label(self):
        """Получить метку для карточки социальных сетей"""

        label = u''
        if self.section_category.slug in ['critic', 'recipe']:
            label = self.section_category.title

        return label or super(Article, self).get_social_label()


@material_register_signals
class TildaArticle(news_models.TildaArticleAbstract):
    """Статья обеда (Тильда)"""

    class Meta(news_models.TildaArticleAbstract.Meta):
        verbose_name = u'статья обеда (Тильда)'
        verbose_name_plural = u'статьи обеда (Тильда)'

    @staticmethod
    def get_material_url(material):
        kwargs = {
            'year': material.stamp.year,
            'month': '%02d' % material.stamp.month,
            'day': '%02d' % material.stamp.day,
            'slug': material.slug,
        }
        return reverse('obed:tilda:read', kwargs=kwargs)


@material_register_signals
class Review(Article):
    """ Рецензии """

    COLUMNIST_CHOICES = (
        ('siropova', u'Лиза Сиропова'),
        ('abram', u'Абрам Дюрсо'),
        ('buuzin', u'Михаил Буузин'),
        ('chesnok', u'Анатолий Чесноков'),
        ('olivie', u'Константин Оливье'),
        ('anteater', u'Аркадий Муравьед'),
        ('grill', u'Ева Гриль'),
        ('terkin', u'Пётр Тёркин'),
        ('guest', u'Мнение гостя'),
    )

    establishment = models.ForeignKey(Establishment, null=True, blank=True, verbose_name=u'Заведение')
    obed_article_ptr = models.OneToOneField(Article, parent_link=True, related_name='obed_review')
    kitchen = models.SmallIntegerField(u'Оценка кухни', default=0)
    service = models.SmallIntegerField(u'Оценка сервиса', default=0)
    environment = models.SmallIntegerField(u'Оценка обстановки', default=0)
    total = models.FloatField(u'итоговая оценка', default=0)
    conclusion = models.TextField(u'Заключение', blank=True)
    resume = models.TextField(u'Резюме', null=True, blank=True)
    columnist = models.CharField(u'Рецензент', max_length=20, choices=COLUMNIST_CHOICES, null=True, blank=True)

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    class Meta:
        verbose_name = u'обзор'
        verbose_name_plural = u'обзоры'

    def save(self, *args, **kwargs):
        self.total = float(self.kitchen + self.service + self.environment) / 3
        super(Review, self).save(*args, **kwargs)


@material_register_signals
class Poll(polls_models.Poll):
    class Meta:
        proxy = True
        verbose_name = u'голосование'
        verbose_name_plural = u'голосования раздела'


@material_register_signals
class Test(testing_models.Test):
    class Meta:
        proxy = True
        verbose_name = u'тест'
        verbose_name_plural = u'тесты раздела'


class Dish(models.Model):
    """ Блюдо """

    # Оценка
    MARK_AWFUL = 1
    MARK_BAD = 2
    MARK_NORMAL = 3
    MARK_GOOD = 4
    MARK_EXCELLENT = 5
    MARK_CHOICES = (
        (MARK_AWFUL, u'Ужасно'),
        (MARK_BAD, u'Плохо'),
        (MARK_NORMAL, u'Ниже среднего'),
        (MARK_GOOD, u'Хорошо'),
        (MARK_EXCELLENT, u'Отлично'),
    )

    name = models.CharField(u'Название', max_length=255)
    price = models.IntegerField(u'Цена', blank=True, null=True, default=0)
    description = models.TextField(u'Описание')
    mark = models.PositiveSmallIntegerField(u'Оценка', choices=MARK_CHOICES, blank=True, null=True)
    review = models.ForeignKey(Review, verbose_name=u'Рецензия', related_name='review_dishes')

    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'блюдо'
        verbose_name_plural = u'блюда'

    def __unicode__(self):
        return self.name


class GuruCause(models.Model):
    """ Справочник для гуру (повод) """

    name = models.CharField(max_length=255, verbose_name=u'Название')
    position = models.PositiveIntegerField(verbose_name=u'Позиция', default=0)
    establishments = models.ManyToManyField(Establishment, blank=True, verbose_name=u'заведения')
    is_dinner = models.BooleanField(
        u'ужин', default=False, db_index=True, blank=True, help_text=u'используется в фильтре "Ужин"'
    )

    class Meta:
        verbose_name = u'запись'
        verbose_name_plural = u'Гуру (повод)'
        ordering = ('position',)

    def __unicode__(self):
        return self.name


class Award(models.Model):
    """Награда"""

    title = models.CharField(u'название', max_length=100, blank=True)
    caption = models.CharField(u'подпись', max_length=40, blank=True)
    icon = FileRemovableField(u'иконка', upload_to='img/site/obed/award', blank=True, null=True)
    created = models.DateTimeField(u'создана', auto_now_add=True)

    establishment = models.ForeignKey(Establishment, verbose_name=u'Заведение', null=True, blank=True)

    class Meta:
        verbose_name = u'награда'
        verbose_name_plural = u'награды'

    def __unicode__(self):
        return self.title
