# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User

from utils.fields.file import FileRemovableField, ImageRemovableField
from utils.db.models.fields.color import ColorField


class Section(models.Model):
    """Раздел"""

    is_general = models.BooleanField('Весь сайт', default=False)

    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('Алиас', max_length=100, unique=True)
    position = models.IntegerField('Позиция', default=0)
    statistic_date = models.DateField('Статистика за', null=True)
    in_audience = models.BooleanField(
        'Выводить в аудитории', default=False, db_index=True)
    in_mediakit = models.BooleanField(
        'Выводить в медиаките', default=False, db_index=True)

    device_pc_percent = models.FloatField('Процент пк', default=0)
    device_mobile_percent = models.FloatField('Процент мобильные', default=0)

    audience_text = models.TextField(
        'Текст для раздела аудитории', blank=True)
    mediakit_title = models.CharField('Название', max_length=100, blank=True)
    mediakit_color = ColorField('Цвет', blank=True, null=True)
    mediakit_main_screenshot = ImageRemovableField(upload_to='img/site/about/mediakit', blank=True, null=True,
                                                verbose_name='Главный скриншот')

    mediakit_attraction_title = models.CharField('Заголовок страницы в привликательности раздела', max_length=100,
                                                 blank=True)
    mediakit_attraction_screenshot = ImageRemovableField(upload_to='img/site/about/mediakit', blank=True, null=True,
                                                      verbose_name='Скриншот в привликательности раздела')
    mediakit_attraction_text = models.TextField(
        'Текст для блока привлекательности раздела', blank=True)

    mediakit_statistic_title = models.CharField(
        'Заголовок страницы статистики', max_length=100, blank=True)

    mediakit_audience_title = models.CharField(
        'Заголовок страницы аудитори', max_length=100, blank=True)

    mediakit_benefit_title = models.CharField(
        'Заголовок страницы наиболее полезен', max_length=100, blank=True)
    mediakit_benefit_text = models.TextField(
        'Текст для блока наиболее полезен', blank=True)

    pages = models.ManyToManyField(
        'Page', blank=True, verbose_name='Связаные прайсы')

    class Meta:
        verbose_name = 'раздел'
        verbose_name_plural = 'разделы'
        ordering = ('position',)

    def __str__(self):
        return self.name


class AgeGenderPercent(models.Model):
    """Демографическая статистика"""

    AGE_18 = 1
    AGE_18_24 = 2
    AGE_25_34 = 3
    AGE_35_44 = 4
    AGE_45_54 = 5
    AGE_55 = 6

    AGE_CHOICES = (
        (AGE_18, 'младше 18'),
        (AGE_18_24, '18-24'),
        (AGE_25_34, '25-34'),
        (AGE_35_44, '35-44'),
        (AGE_45_54, '45-54'),
        (AGE_55, '55 и старше'),
    )

    GENDER_MAN = 1
    GENDER_WOMAN = 2

    GENDER_CHOICES = (
        (GENDER_MAN, 'Мужчина'),
        (GENDER_WOMAN, 'Женщина'),
    )

    section = models.ForeignKey(Section, related_name='agegenderpercents', on_delete=models.CASCADE)
    age = models.IntegerField('Возраст', choices=AGE_CHOICES, default=AGE_18)
    gender = models.IntegerField(
        'Пол', choices=GENDER_CHOICES, default=GENDER_MAN)
    percent = models.FloatField('Процент', default=0)

    class Meta:
        verbose_name = 'возраст-пол'
        verbose_name_plural = 'возраст-пол'
        ordering = ('section', 'age', 'gender')

    def __str__(self):
        """ !TODO:
                - Незнаю откуда порождаются методы:
                    - get_gender_display
                    - get_age_display
        """
        # return u'{} {} {} {}%'.format(self.section, self.get_gender_display(), self.get_age_display(), self.percent)
        return self.section


class Interest(models.Model):
    """Статистика интересов"""

    section = models.ForeignKey(Section, related_name='interests', on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=100)
    percent = models.FloatField('Процент', default=0)

    class Meta:
        verbose_name = 'интерес'
        verbose_name_plural = 'интересы'
        ordering = ('percent',)

    def __str__(self):
        return '{} {} {}%'.format(self.section, self.name, self.percent)


class Faq(models.Model):
    """Вопросы ответы"""

    name = models.CharField('Название', max_length=100)
    position = models.IntegerField(verbose_name='Позиция', default=0)
    text = models.TextField('Содержание')

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ('position',)

    def __unicode__(self):
        return self.name


class Condition(models.Model):
    """Требования к рекламе"""

    name = models.CharField('Название', max_length=100)
    position = models.IntegerField('Позиция', default=0)
    text = models.TextField('Содержание')

    class Meta:
        verbose_name = 'требование к рекламе'
        verbose_name_plural = 'требования к рекламе'
        ordering = ('position',)

    def __str__(self):
        return self.name


class Page(models.Model):
    """Прайс"""

    ON_PC = 1
    ON_MOBILE = 2

    DEVICE_CHOICES = (
        (ON_PC, u'на компьютерах'),
        (ON_MOBILE, u'на мобильных устройствах'),
    )

    name = models.CharField(u'Раздел', max_length=100)
    image = models.ImageField(
        u'Шаблон', upload_to='img/site/price', blank=True)
    position = models.IntegerField(u'Позиция', unique=False)
    view_count_day = models.IntegerField(
        u'Количество просмотров за день', default=0)
    view_count_week = models.IntegerField(
        u'Количество просмотров за неделю', default=0)
    view_count_month = models.IntegerField(
        u'Количество просмотров за месяц', default=0)
    unique_user_count_day = models.IntegerField(
        u'Количество уникальных пользователей за день', default=0)
    unique_user_count_week = models.IntegerField(
        u'Количество уникальных пользователей за неделю', default=0)
    unique_user_count_month = models.IntegerField(
        u'Количество уникальных пользователей за месяц', default=0)
    visible = models.BooleanField(
        u'Выводить на сайте', default=True, db_index=True)
    device = models.IntegerField(
        u'Тип устройства', choices=DEVICE_CHOICES, default=ON_PC, db_index=True)

    class Meta:
        db_table = 'company_page'
        verbose_name = u'прайс'
        verbose_name_plural = u'прайсы'
        ordering = ('position',)

    def __str__(self):
        """ !TODO:
                - Незнаю откуда порождаются методы:
                    - get_device_display
                    - get_age_display
        """
        return self.name


class Pricefile(models.Model):
    """Файл прайса"""

    name = models.CharField(u'Название', max_length=255, blank=True, null=True)
    slug = models.SlugField(u'Алиас', blank=True, null=True)
    file = FileRemovableField(verbose_name=u'Прайс',
                              upload_to="img/site/about/price/")

    class Meta:
        db_table = 'company_pricefile'
        verbose_name = u'файл прайса'
        verbose_name_plural = u'файлы прайсов'

    def __str__(self):
        return self.name


class Price(models.Model):
    """Цена"""

    WEEK_PERIOD = 1
    ONCE_PERIOD = 2
    DAY_PERIOD = 3
    MONTH_PERIOD = 4
    MONTH_PUB_PERIOD = 5
    HALF_YEAR_PERIOD = 6
    YEAR_PERIOD = 7
    TWO_DAY_PERIOD = 8

    PERIOD = (
        (WEEK_PERIOD, u'за неделю'),
        (ONCE_PERIOD, u'за публикацию'),
        (DAY_PERIOD, u'за сутки'),
        (TWO_DAY_PERIOD, u'за 2 суток'),
        (MONTH_PERIOD, u'за месяц'),
        (MONTH_PUB_PERIOD, u'мес. со статьей'),
        (HALF_YEAR_PERIOD, u'за 6 мес.'),
        (YEAR_PERIOD, u'за 12 мес.'),
    )

    TOP_POSITION = 1
    BOTTOM_POSITION = 2
    RIGHT_POSITION = 3
    LEFT_POSITION = 4

    POSITION = (
        (TOP_POSITION, u'сверху'),
        (BOTTOM_POSITION, u'снизу'),
        (RIGHT_POSITION, u'справа'),
        (LEFT_POSITION, u'слева'),
    )

    page = models.ForeignKey('Page', on_delete=models.CASCADE)
    format = models.CharField(max_length=100, verbose_name=u'Формат')
    period = models.IntegerField(
        u'Период размещения', choices=PERIOD, default=WEEK_PERIOD)
    marker_position = models.IntegerField(
        u'Позиция маркера', choices=POSITION, default=TOP_POSITION)
    place = models.CharField(max_length=100, verbose_name=u'Место')
    value = models.CharField(max_length=100, verbose_name=u'Цена')
    coordinate_top_left = models.CharField(max_length=11, verbose_name=u'Координата верхнего левого угла',
                                           help_text=u'Например: 230,340', default=u'0,0')
    height_width = models.CharField(max_length=11, verbose_name=u'Высота и длинна', help_text=u'Например: 100,200',
                                    default=u'0,0')
    condition = models.ForeignKey(
        Condition, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=u'Требование'
    )
    description = models.TextField(u'Описание', blank=True)
    recommendation = models.TextField(u'Рекомендация', blank=True)

    class Meta:
        db_table = 'company_price'
        verbose_name = u'цена'
        verbose_name_plural = u'цены'

    def __str__(self):
        return self.place


class Vacancy(models.Model):
    """Вакансия"""

    NON_TEST = 1
    OPT_TEST = 2
    OFF_TEST = 3
    TESTS = (
        (NON_TEST, u'не нужно'),
        (OPT_TEST, u'Высылается дополнительно'),
        (OFF_TEST, u'На собеседовании')
    )

    name = models.CharField(u'Название', max_length=255)
    end_date = models.DateField(u'Прием заявок до', blank=True, null=True)
    start_date = models.DateField(u'Размещена', auto_now_add=True)
    update_date = models.DateField(u'Последнее обновление', auto_now=True)

    main_requirements = models.TextField(u'Основные требования')
    optons_requirements = models.TextField(
        u'Дополнительные требования', blank=True)
    test = models.IntegerField(
        u'Тестовое задание', choices=TESTS, default=NON_TEST)

    class Meta:
        db_table = 'company_vacancy'
        verbose_name = u'вакансию'
        verbose_name_plural = u'вакансии'

    def is_new(self):
        """Вакансия старше недели"""

        now = datetime.datetime.now().date()
        result = False
        if (now - self.start_date) <= datetime.timedelta(7):
            result = True

        return result

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Сотрудник компании"""

    title = models.CharField(u'Ф.И.О.', max_length=255)
    job = models.CharField(u'Должность', max_length=255)
    email = models.EmailField(u'Почта')
    photo = ImageRemovableField(
        upload_to='img/site/employees', verbose_name=u'Фотография')
    position = models.PositiveIntegerField(u'Позиция', default=0)
    is_op = models.BooleanField(u'Сотрудник отдела продаж', default=False)
    is_head_op = models.BooleanField(u'Начальник отдела продаж', default=False)

    class Meta:
        db_table = 'company_employees'
        verbose_name = u'сотрудник'
        verbose_name_plural = u'сотрудники'
        ordering = ('position',)

    def __str__(self):
        return self.title


class Question(models.Model):
    """Вопрос пользователя"""

    name = models.CharField(u'Имя', max_length=255, blank=True)
    email = models.EmailField(u'E-mail')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                             verbose_name=u'Автор', related_name='questions')
    content = models.TextField(u'Содержание')
    ip = models.PositiveIntegerField(u'IP адрес')
    user_agent = models.TextField(u'User Agent')
    created = models.DateTimeField(u'Когда спросили')
    respondent = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Респондент',
                                   related_name='question_replies', on_delete=models.CASCADE)
    reply = models.TextField(u'Ответ', blank=True)
    replied = models.DateTimeField(u'Дата ответа', blank=True, null=True)
    attach = FileRemovableField(verbose_name=u'Прикрепленный файл', upload_to="img/site/about/attach/",
                                blank=True, null=True)
    is_replied = models.BooleanField(u'Ответили', default=False)

    class Meta:
        db_table = 'company_questions'
        verbose_name = u'вопрос'
        verbose_name_plural = u'вопросы'
