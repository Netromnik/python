# -*- coding: utf-8 -*-

import datetime
import os
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.utils.functional import cached_property

from irk.afisha import managers
from irk.afisha import settings as app_settings
from irk.afisha.cache import invalidate
from irk.afisha.managers import AnnouncementQuerySet, PrismQuerySet, TicketEventQuerySet
from irk.afisha.schedule import Schedule
from irk.afisha.search import EventSearch, GuideSearch
from irk.afisha.sessions import add_cache_rows, delete_cache_rows, update_cache_table, update_schedule_specified
from irk.comments.models import CommentMixin
from irk.gallery.fields import ManyToGallerysField
from irk.invoice.models import Invoice, BaseOrder
from irk.news import models as news_models
from irk.news.managers import BaseMaterialManager, LongreadMaterialManager, MaterialManager, MagazineMaterialManager
from irk.news.models import material_register_signals
from irk.options.models import Site
from irk.phones.models import Firms, SectionFirm, Sections
from irk.polls import models as polls_models
from irk.testing import models as testing_models
from irk.utils.fields.file import FileRemovableField, ImageRemovableField

FILM_TYPE = 2


class ScheduleModel(models.Model):
    """ Все модели которые имеют расписание наследуются от этой модели """

    def __init__(self, *args, **kwargs):
        self.schedule = Schedule(self)
        super(ScheduleModel, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True


class EventType(models.Model):
    """Тип события"""

    title = models.CharField(u'Название', max_length=255)
    title2 = models.CharField(u'Название (В)', max_length=255, blank=True)
    alias = models.SlugField(u'Алиас')
    position = models.IntegerField(u'Позиция', default=0, db_index=True, blank=True)
    on_index = models.BooleanField(u'Показывать в главной ленте', db_index=True, default=True)
    hide_past = models.BooleanField(u'Скрывать прошедшие события', db_index=True, default=False)
    is_visible = models.BooleanField(u'Показывать в главном меню', db_index=True, default=True)

    class Meta:
        db_table = u'afisha_sections'
        verbose_name = u'тип события'
        verbose_name_plural = u'типы'

    def __unicode__(self):
        return self.title


class Genre(models.Model):
    """Жанр события"""

    name = models.CharField(u'Название', max_length=255)

    class Meta:
        db_table = u'afisha_genre'
        verbose_name = u'жанр'
        verbose_name_plural = u'жанры'

    def __unicode__(self):
        return self.name if self.name else ''


def upload_to(object, filename):
    folder = Guide.objects.count() / 500 + 1
    return 'img/site/afisha/%s/%s' % (folder, filename)


class Guide(ScheduleModel, SectionFirm):
    """Гид"""

    title_short = models.CharField(u'Короткое название', max_length=255, blank=True)
    main_phones = models.CharField(u'Телефоны для смс', max_length=255, blank=True)
    kitchen_type = models.CharField(u'Тип кухни', max_length=255, default=0, editable=False)
    price_type = models.IntegerField(default=0, editable=False)
    event_type = models.ForeignKey(EventType, verbose_name=u'Тип событий.', null=True)
    map = ImageRemovableField(upload_to='img/site/afisha/maps', verbose_name=u'Схема зала', blank=True,  null=True)
    obed_address = models.CharField(max_length=255, blank=True)
    obed_id = models.IntegerField(null=True, blank=True)
    article = models.TextField(blank=True, verbose_name=u'Описание')
    menu = models.TextField(blank=True, verbose_name=u'Меню')
    skip_tour_for_sms = models.BooleanField(default=False)
    type_main = models.ForeignKey(Sections, null=True, blank=True)
    image = ImageRemovableField(upload_to=upload_to, verbose_name=u'Изображение', blank=True)
    notice = models.TextField(verbose_name=u'Объявление', blank=True)
    price = models.CharField(u'Цены', max_length=255, blank=True, default=u'')
    price_description = models.TextField(blank=True, verbose_name=u'Описание для цены')

    _sessions_ = None

    search = GuideSearch()

    class Meta:
        verbose_name = u'заведение'
        verbose_name_plural = u'заведения гида'

    def get_absolute_url(self):
        if self.id:
            self.pk = self.id
        return reverse('guide:read', args=(self.pk,))

    def get_sessions(self, date=None, hall=None):
        """
            @param date: дата относительно которой выбираются сенсы
            @param hall: зал
        """

        if not self._sessions_ or date or hall:
            if hall:
                event_guide_filter = {'hall': hall}
            else:
                event_guide_filter = {}

            from irk.afisha.helpers import Sessions as ObjectSessions
            self._sessions_ = ObjectSessions(
                self, date=date or datetime.datetime.now().date(),
                event_guide_filter=event_guide_filter)
        return self._sessions_
    sessions = property(get_sessions)

    def get_comment_object(self):
        return self.firm
    comment_object = property(get_comment_object)

    def __unicode__(self):
        if self.title_short:
            return self.title_short
        else:
            return super(Guide, self).__unicode__()

    def is_tickets_exist(self):
        """Есть сеансы на которые можно купить билет"""
        return CurrentSession.objects.filter(guide=self, is_hidden=False, real_date__gte=datetime.datetime.now()) \
            .filter(Q(ramblersession__isnull=False) | Q(kassysession__isnull=False)) \
            .exists()
            # Q(kinomaxsession__isnull=False) |


class GuideFirm(Firms):
    """Прокси-модель для фирм. привязанных к гиду"""

    class Meta:
        proxy = True

    @models.permalink
    def get_absolute_url(self):
        return reverse('guide', (), {'guide_id': self.guide.pk})


class Hall(models.Model):
    guide = models.ForeignKey(Guide)
    name = models.CharField(u'Название', max_length=255)
    num_places = models.PositiveIntegerField(u'Кол-во мест', null=True, blank=True)
    map = ImageRemovableField(upload_to='img/site/afisha/maps', verbose_name=u'Схема зала', blank=True, null=True)
    position = models.SmallIntegerField(null=True, verbose_name=u'Позиция')
    price = models.CharField(u'Цены', max_length=255, blank=True, default=u'')

    class Meta:
        verbose_name = u'зал'

    def __unicode__(self):
        return self.name or ''

    def get_absolute_url(self):
        return '%s?hall=%s' % (self.guide.get_absolute_url(), self.pk)


def image_upload_to(instance, filename):
    """Вернуть путь для сохранения широкоформатной фотографии"""

    opts = instance._meta

    return 'img/site/afisha/{model_name}/{folder}/{filename}{ext}'.format(
        model_name=opts.model_name,
        folder=opts.model.objects.count() / 1024,
        filename=str(uuid.uuid4()),
        ext=os.path.splitext(filename)[1],
    )


class Event(CommentMixin, ScheduleModel, models.Model):
    """Событие афиши"""

    AGE_CHOICES = map(
        lambda x: (x, '%s+' % x),
        [0, 6, 12, 16, 18, 21]
    )

    type = models.ForeignKey(EventType, verbose_name=u'Тип события')
    parent = models.ForeignKey('self', blank=True, null=True, limit_choices_to={'parent__isnull': True})
    title = models.CharField(u'Название', max_length=255)
    caption = models.TextField(u'Подводка', blank=True)
    original_title = models.CharField(u'оригинальное название', max_length=255, blank=True)
    genre = models.ForeignKey(Genre, db_column='genreID', verbose_name=u'Жанр', blank=True, null=True)
    duration = models.CharField(u'Длительность', max_length=255, blank=True, null=True,
                                help_text=u'Указывается для кино, концертов, спектаклей и т.д.')
    production = models.CharField(u'Производство', max_length=255, blank=True,
                                  help_text=u'Указывается только для кино.')
    info = models.TextField(u'Доп. инфо', blank=True, help_text=u'Режисёры, актёры. Болд никогда здесь не используем!')
    content = models.TextField(u'Описание', blank=True)
    comments_cnt = models.IntegerField(null=True, editable=False)
    last_comment_id = models.IntegerField(null=True, editable=False)
    video = models.TextField(u'Видео', blank=True, help_text=u'HTML код')
    age_rating = models.SmallIntegerField(verbose_name=u'Возрастной рейтинг', choices=AGE_CHOICES, default=None,
                                          null=True, blank=True)
    premiere_date = models.CharField(verbose_name=u'Дата премьеры', blank=True, max_length=255)
    is_hidden = models.BooleanField(u'Скрыто', default=True)
    author_ip = models.PositiveIntegerField(u'IP автора', null=True, blank=True, default=None)
    created = models.DateTimeField(u'Дата создания', default=datetime.datetime.now)
    buy_btn_clicks = models.PositiveIntegerField(u'Клики по кнопке купить', default=0)

    # События добавленные пользователем
    is_user_added = models.BooleanField(u'Добавлено пользователем', default=False)
    is_commercial = models.BooleanField(u'Коммерческое предложение', default=False)
    organizer = models.CharField(u'Организатор', max_length=255, blank=True, default='')
    organizer_email = models.EmailField(u'E-mail организатора', blank=True, default='')
    organizer_contacts = models.CharField(u'Контакты организатора', max_length=1024, blank=True, default='')
    is_approved = models.BooleanField(u'Коммерческое предложение одобрено', default=False)

    imdb_id = models.CharField(u'Идентификатор в IMDB', max_length=10, blank=True)
    imdb_rate = models.FloatField(u'Рейтинг IMDB', blank=True, null=True)

    # Ссылки на соцсети
    source_url = models.URLField(u'Ссылка на официальный сайт', blank=True, default='')
    vk_url = models.CharField(u'Ссылка на Вконтакте', max_length=255, blank=True, default='')
    fb_url = models.CharField(u'Ссылка на Facebook', max_length=255, blank=True, default='')
    ok_url = models.CharField(u'Ссылка на Однокласники', max_length=255, blank=True, default='')
    inst_url = models.CharField(u'Ссылка на Instagram', max_length=255, blank=True, default='')

    gallery = ManyToGallerysField(
        help_text=u'Файлы - не более 300х270 и не менее 100x60 пикс., jpeg или gif, до 25 КБ.')
    sites = models.ManyToManyField(
        Site, related_name='events', db_table='afisha_sites_events', blank=True, verbose_name=u'Разделы'
    )

    wide_image = models.ImageField(
        verbose_name=u'Широкоформатная фотография', upload_to=image_upload_to, help_text=u'Размер: 960х454 пикселей',
        blank=True
    )
    prisms = models.ManyToManyField('Prism', related_name='events', blank=True, verbose_name=u'Призмы')

    objects = managers.EventManager()
    _sessions_ = None

    search = EventSearch()

    comments_filter = ('type',)

    __original_is_approved = None
    __original_is_hidden = None

    class Meta:
        verbose_name = u'событие'
        verbose_name_plural = u'события'

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.__original_is_approved = self.is_approved
        self.__original_is_hidden = self.is_hidden

    def save(self, *args, **kwargs):
        from irk.afisha.order_helpers import EventOrderHelper
        from irk.afisha.helpers import sent_event_open_notif

        # Создать платеж если событие одобрено
        if self.is_commercial and self.is_approved and self.is_approved != self.__original_is_approved:
            order = EventOrderHelper(self)
            order.create_invoice()

        # Уведомление о размещении события пользователю
        if not self.is_hidden and self.is_hidden != self.__original_is_hidden:
            sent_event_open_notif(self)

        return super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # если есть расписание, то дата в урле будут
        # по дате первой привязки

        if hasattr(self, 'schedule') and type(self.schedule) in [tuple, list]:
            if 'sessions' in self.schedule[0] and self.schedule[0]['sessions']:
                date = self.schedule[0]['sessions'][0].date
            else:
                date = self.schedule[0]['date']
        elif hasattr(self, 'schedule') and self.schedule.first:
            date = self.schedule.first.date
        else:
            date = self.sessions.get_nearest_date()

        context = {
            'event_id': self.pk,
            'year': date.year,
            'month': '%02d' % date.month,
            'day': '%02d' % date.day,
            'event_type': self.type.alias
        }
        return reverse('afisha:event_read', kwargs=context)

    @property
    def caption_text(self):
        return self.caption or self.content

    def get_event_guide_set(self):
        try:
            if hasattr(self, 'current_date'):
                date = self.current_date
            else:
                date = self.sessions.get_date()
            qs = self.eventguide_set.filter(period__start_date__lte=date, period__end_date__gte=date)
            for q in qs:
                setattr(q, 'current_date', date)
            return qs
        except Exception:
            pass
    eventguide = property(get_event_guide_set)

    def get_ordered_event_guide_set(self):
        try:
            if hasattr(self, 'current_date'):
                date = self.current_date
            else:
                date = self.sessions.get_date()
            qs = self.eventguide_set.filter(
                period__start_date__lte=date,
                period__end_date__gte=date).annotate(min_time=models.Min('period__sessions__time')).order_by('min_time')
            for q in qs:
                setattr(q, 'current_date', date)
            return qs
        except Exception:
            pass

    def get_sessions(self, date=None, city=None):
        """Сеансы события"""

        if not self._sessions_ or date or city:
            event_guide_filter = {}
            if city:
                event_guide_filter = {'city': city}
            from irk.afisha.helpers import Sessions as ObjectSessions
            self._sessions_ = ObjectSessions(self, date=date or datetime.date.today(),
                                             event_guide_filter=event_guide_filter)

        return self._sessions_

    sessions = property(get_sessions)

    def tickets_sessions(self):
        """Cеансы на которые можно купить билет"""

        return CurrentSession.objects \
            .filter(event=self, is_hidden=False, real_date__gte=datetime.datetime.now()) \
            .filter(Q(ramblersession__isnull=False) | Q(kassysession__isnull=False)) \
            .exclude(ramblersession__is_sale_available=False).order_by('real_date')

    def is_tickets_exist(self):
        """Есть сеансы на которые можно купить билет"""
        return self.tickets_sessions().exists()

    def nearest_tickets_session(self):
        """Ближайший сеанс для события на который можно купить билет"""
        return self.tickets_sessions().first()

    @cached_property
    def is_free(self):
        """Бесплатное событие"""
        return self.prisms.filter(title='Бесплатно').exists()

    @cached_property
    def is_rambler(self):
        """Cобытие рамблер"""
        return RamblerEvent.objects.filter(event_id=self.pk).exists()


post_save.connect(invalidate, sender=Event)
post_save.connect(update_cache_table, sender=Event)


class EventOrder(BaseOrder):
    """Заказ размещения события"""

    event = models.ForeignKey(Event, verbose_name=u'Событие', related_name='eventorder_event')

    def __unicode__(self):
        return u'{}'.format(self.pk)

    class Meta:
        verbose_name = u'Заказ'
        verbose_name_plural = u'Заказы'

    def get_order_helper_class(self):
        from irk.afisha.order_helpers import EventOrderHelper
        return EventOrderHelper


class EventGuide(models.Model):
    SOURCE_MANUAL = 0
    SOURCE_RAMBLER = 1
    SOURCE_KINOMAX = 2
    SOURCE_CHOICES = (
        (SOURCE_MANUAL, 'Вручную'),
        (SOURCE_RAMBLER, 'Рамблер'),
        (SOURCE_KINOMAX, 'Киномакс'),
    )

    guide = models.ForeignKey(Guide, verbose_name=u'Гид', null=True, blank=True)
    guide_name = models.CharField(max_length=255, blank=True)
    main_announcement = models.BooleanField(u'Основной', default=False)  # Не используется
    hall = models.ForeignKey(Hall, null=True, blank=True, verbose_name=u'Зал')
    event = models.ForeignKey(Event)
    source = models.PositiveSmallIntegerField(u'источник', choices=SOURCE_CHOICES, default=SOURCE_MANUAL, db_index=True)

    class Meta:
        verbose_name = u'привязку'
        verbose_name_plural = u'привязка'

    def __unicode__(self):
        return u'Привязка'

    def get_current_period(self):
        return self.period_set.for_date(self.current_date).order_by('-start_date')[0]
    current_period = property(get_current_period)


post_save.connect(update_cache_table, sender=EventGuide)


class Period(models.Model):
    event_guide = models.ForeignKey(EventGuide)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.CharField(max_length=255, blank=True, null=True)
    is_3d = models.BooleanField(default=False, verbose_name=u'3D')
    duration = models.TimeField(null=True, blank=True, verbose_name=u'Длительность')
    objects = managers.PeriodManager()

    def is_day(self):
        return (self.end_date - self.start_date) == datetime.timedelta(0)

    def get_sessions(self):
        return Sessions.objects.filter(period=self).order_by('order_time')
    get_sessions = property(get_sessions)

    @property
    def future_sessions(self):
        return Sessions.objects.filter(period=self, time__gte=datetime.datetime.now().time()).order_by('order_time')

    def get_is_ended(self):
        return self.end_date < datetime.datetime.now().date()
    is_ended = property(get_is_ended)

    def __repr__(self):
        return u'<Period {} - {} {} {}>'.format(
            self.start_date, self.end_date, self.price,
            u'3d' if self.is_3d else u''
        ).encode('utf-8')


post_save.connect(update_cache_table, sender=Period)
post_save.connect(update_schedule_specified, sender=Period)


class Sessions(models.Model):
    ALL = 1
    EXPECTED = 1

    period = models.ForeignKey(Period)
    time = models.TimeField()
    order_time = models.IntegerField(editable=False, db_index=True)
    price = models.CharField(max_length=255, null=True, blank=True)

    objects = managers.SessionsManager()

    class Meta:
        ordering = ('order_time',)

    def __repr__(self):
        return u'<Session {} for period {}>'.format(self.time, self.period_id).encode('utf-8')

    def get_is_expected(self):
        if self.time.hour < 6:
            return True
        return self.time > datetime.datetime.now().time()
    is_expected = property(get_is_expected)

    def save(self, *args, **kwargs):
        hour = self.time.hour if self.time.hour > 6 else self.time.hour + 24
        self.order_time = int('%d%02d' % (hour, self.time.minute))

        super(Sessions, self).save(*args, **kwargs)


post_save.connect(add_cache_rows, sender=Sessions)
post_delete.connect(delete_cache_rows, sender=Sessions)


class CurrentSession(models.Model):
    """ Кэш текущих сеансов событий на 2 недели """

    # Дата проведения события. Если поле `time` меньше 06:00, дата уменьшается на один день.
    date = models.DateField(verbose_name=u'Дата события', db_index=True)
    time = models.TimeField(verbose_name=u'Время', db_index=True, null=True)
    # TODO: описание поля, зачем нужно
    filter_time = models.TimeField(verbose_name=u'Время с учетом длительности', db_index=True, null=True)
    fake_date = models.DateTimeField(verbose_name=u'Время события', db_index=True)  # Равна `date` + `time`
    # Действительная дата начала события
    real_date = models.DateTimeField(verbose_name=u'Реальная дата', db_index=True)
    # Действительная дата окончания события
    end_date = models.DateTimeField(verbose_name=u'Дата окончания', db_index=True)  # Равна `real_date` + `period.duration`
    event_type = models.ForeignKey(EventType)
    event_guide = models.ForeignKey(EventGuide)
    event = models.ForeignKey(Event)
    guide = models.ForeignKey(Guide, null=True,)
    period = models.ForeignKey(Period)
    hall = models.ForeignKey(Hall, null=True, blank=True)
    is_hidden = models.BooleanField(default=False)
    is_3d = models.BooleanField(default=False)
    min_price = models.IntegerField(u'Цена от', null=True)

    objects = managers.CurrentSessionQuerySet.as_manager()

    class Meta:
        verbose_name = u'запись'
        verbose_name_plural = u'кэш'
        db_table = 'afisha_current_sessions'

    def __unicode__(self):
        return u'{0.time:%H:%M} {0.date:%d.%m.%y} {0.event}'.format(self)

    @property
    def kassy_session(self):
        """
        Связанный объект KassySession

        Если связанного объекта нет, возвращается None
        """

        if hasattr(self, 'kassysession'):
            return self.kassysession

    @property
    def rambler_session(self):
        """Связанный объект RamblerSession"""

        if hasattr(self, 'ramblersession') and self.ramblersession.is_sale_available:
            return self.ramblersession

    @property
    def kinomax_session(self):
        """
        Связанный объект KinomaxSession

        Если связанного объекта нет, возвращается None
        """

        if hasattr(self, 'kinomaxsession'):
            return self.kinomaxsession

    def is_tickets_exist(self):
        """Есть билет онлайн"""

        if self.rambler_session or self.kassy_session:
            return True


class Prism(models.Model):
    """
    Призмы для рубрикатора афиши
    """

    title = models.CharField(max_length=50, verbose_name=u'Название')
    icon = FileRemovableField(u'иконка', upload_to='img/site/afisha/prism', blank=True, null=True)
    svg = models.TextField(u'svg', blank=True)
    position = models.PositiveSmallIntegerField(verbose_name=u'Позиция', blank=True, default=0)
    is_hidden = models.BooleanField(verbose_name=u'Скрыто', default=False)

    objects = PrismQuerySet.as_manager()

    class Meta:
        verbose_name = u'призма'
        verbose_name_plural = u'призмы'
        ordering = ['position', '-id']

    def __unicode__(self):
        return self.title


class AnnouncementColor(models.Model):
    """ Цвета для анонсов """

    value = models.CharField(max_length=6, verbose_name=u'Цвет')
    position = models.SmallIntegerField(verbose_name=u'Позиция', blank=True)

    class Meta:
        verbose_name = u'цвет'
        verbose_name_plural = u'цвета'

    def save(self, *args, **kwargs):
        if not self.position:
            self.position = AnnouncementColor.objects.count() + 1
        return super(AnnouncementColor, self).save(*args, **kwargs)


class AnnouncementMixin(models.Model):
    """Примесь для материалов отображаемых в блоке анонсов (слайдер)"""

    is_announce = models.BooleanField(
        u'анонсировать', db_index=True, default=False, help_text=u'Материал попадет в слайдер анонсов'
    )

    class Meta:
        abstract = True


class Announcement(models.Model):
    """Анонс"""

    PLACE_AFISHA_INDEX = 1
    PLACE_AFISHA_TYPE_PAGE = 2
    PLACE_HOME_SLIDER = 3
    PLACE_CHOICES = (
        (PLACE_AFISHA_INDEX, u'Слайдер на главной Афиши'),
        (PLACE_AFISHA_TYPE_PAGE, u'Слайдер подразделов Афиши'),
        (PLACE_HOME_SLIDER, u'Слайдер на главной'),
    )

    event = models.ForeignKey(Event, verbose_name=u'событие', related_name='announcements')
    place = models.PositiveSmallIntegerField(
        u'место', choices=PLACE_CHOICES, db_index=True, null=True, blank=True,
        help_text=u'Если не указано, анонс выводится везде'
    )
    start = models.DateField(u'начало', db_index=True)
    end = models.DateField(u'конец', db_index=True)

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        verbose_name = u'анонс'
        verbose_name_plural = u'анонсы'

    def __unicode__(self):
        if self.start == self.end:
            return self.start.strftime('%d.%m.%Y')
        else:
            return u'{0.start:%d.%m.%Y} - {0.end:%d.%m.%Y}'.format(self)


@material_register_signals
class Review(AnnouncementMixin, news_models.Article):
    """ Для рецензий на фильмы используем статьи  """

    article_ptr = models.OneToOneField('news.Article', parent_link=True, related_name='afisha_reviews')
    event = models.ForeignKey(Event, verbose_name=u'Событие', related_name='review')

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    class Meta:
        db_table = 'afisha_review'
        verbose_name = u'рецензия'
        verbose_name_plural = u'рецензии'

    # ревью афиши, привязанные к спецпроекту, не должны менять урл
    def get_absolute_url(self):
        return self.get_material_url(self)


@material_register_signals
class Article(AnnouncementMixin, news_models.Article):
    """Статьи афиши"""

    article_ptr = models.OneToOneField('news.Article', parent_link=True, related_name='afisha_articles')

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    class Meta:
        verbose_name = u'статья'
        verbose_name_plural = u'статьи'


@material_register_signals
class Photo(AnnouncementMixin, news_models.Photo):
    """Фоторепы афиши"""

    photo_ptr = models.OneToOneField('news.Photo', parent_link=True, related_name='afisha_photos')

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    class Meta:
        verbose_name = u'фоторепортаж'
        verbose_name_plural = u'фоторепортажи'


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


class TicketBuilding(models.Model):
    """Заведение в билетной системе"""

    created = models.DateTimeField(u'создано', auto_now_add=True)
    modified = models.DateTimeField(u'изменено', auto_now=True)
    guide = models.OneToOneField(
        'afisha.Guide', on_delete=models.SET_NULL, verbose_name=u'заведение гида', null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def __repr__(self):
        return u'<{} {} {}>'.format(self.__class__.__name__, self.id, self.__unicode__()).encode('utf-8')


class TicketHall(models.Model):
    """Зал в билетной системе"""

    created = models.DateTimeField(u'создано', auto_now_add=True)
    modified = models.DateTimeField(u'изменено', auto_now=True)
    hall = models.OneToOneField(
        'afisha.Hall', on_delete=models.SET_NULL, verbose_name=u'зал', null=True, blank=True
    )

    class Meta:
        abstract = True

    def __repr__(self):
        return u'<{} {} {}>'.format(self.__class__.__name__, self.id, self.__unicode__()).encode('utf-8')


class TicketEvent(models.Model):
    """Событие в билетной системе"""

    date_start = models.DateTimeField(u'дата начала', null=True, db_index=True)
    created = models.DateTimeField(u'создано', auto_now_add=True)
    modified = models.DateTimeField(u'изменено', auto_now=True)
    event = models.ForeignKey(
        'afisha.Event', on_delete=models.SET_NULL, verbose_name=u'событие', null=True, blank=True
    )

    class Meta:
        abstract = True

    def ticket_label(self):
        """Метка билетной системы. Необходима для правильного связывания событий"""
        raise NotImplementedError

    def __repr__(self):
        return u'<{} {} {}>'.format(self.__class__.__name__, self.id, self.__unicode__()).encode('utf-8')

    @cached_property
    def nearest_session(self):
        """Ближайший сеанс для события"""

        now = datetime.datetime.now()

        return self.sessions.filter(show_datetime__gte=now).order_by('show_datetime').first()


class TicketSession(models.Model):
    """Сеанс в билетной системе"""

    datetime = models.DateTimeField(u'дата и время', null=True, db_index=True)
    # show_datetime используется для отображения ночных сеансов. В афише ночные сеансы отображаются предыдущим днём.
    # Ex.: If datetime = 09.06.2017 01:00, than show_datetime = 08.06.2017 01:00
    show_datetime = models.DateTimeField(u'отображаемые дата и время', null=True, db_index=True)
    created = models.DateTimeField(u'создано', auto_now_add=True)
    modified = models.DateTimeField(u'изменено', auto_now=True)
    current_session = models.OneToOneField(
        'afisha.CurrentSession', on_delete=models.SET_NULL, verbose_name=u'сеанс', null=True,
        blank=True
    )
    # is_ignore нужен, когда сеанс неверный или дубликат другого сеанса (из-за ошибок билетной системы)
    # Если is_ignore = True, то этот сеанс не связывается с current_session
    is_ignore = models.BooleanField(u'игнорировать', default=False, db_index=True)

    class Meta:
        abstract = True
        get_latest_by = 'datetime'

    def __repr__(self):
        return u'<{} {} {}>'.format(self.__class__.__name__, self.id, self.__unicode__()).encode('utf-8')

    def __unicode__(self):
        return u'{0.id} {0.datetime:%d.%m.%y %H:%M}'.format(self)


class KassyRollerman(models.Model):
    """Организатор"""

    id = models.IntegerField(u'ID', primary_key=True)
    name = models.CharField(u'название', max_length=255)
    email = models.CharField(u'email', max_length=255)
    address = models.CharField(u'адрес', max_length=255)
    phone = models.CharField(u'телефон', max_length=255)
    inn = models.CharField(u'ИНН', max_length=255)
    okpo = models.CharField(u'ОКПО', max_length=255)
    state = models.BooleanField(u'активно', default=True, db_index=True)

    created = models.DateTimeField(u'создано', auto_now_add=True)
    modified = models.DateTimeField(u'изменено', auto_now=True)

    class Meta:
        verbose_name = u'организатор в kassy.ru'
        verbose_name_plural = u'организаторы в kassy.ru'

    def __unicode__(self):
        return self.name


class KassyBuilding(TicketBuilding):
    """Учреждение (площадки и кассы)"""

    id = models.IntegerField(u'ID', primary_key=True)
    type_id = models.IntegerField(u'id типа учреждения', null=True)
    region_id = models.IntegerField(u'id региона', null=True)       # 41 - Иркутская область
    title = models.CharField(u'название', max_length=255)
    descr = models.TextField(u'описание')
    address = models.CharField(u'адрес', max_length=255)
    phone = models.CharField(u'телефон', max_length=255)
    url = models.CharField(u'сайт', max_length=255)
    workhrs = models.CharField(u'часы работы', max_length=255)
    hall_count = models.IntegerField(u'количество залов', null=True)
    marginprc = models.IntegerField(u'процент наценки', null=True)
    geo_lat = models.FloatField(u'географическая широта', null=True)
    geo_lng = models.FloatField(u'географическая долгота', null=True)
    is_sale = models.BooleanField(u'продажи разрешены', default=True, db_index=True)
    is_reserv = models.BooleanField(u'бронирование разрешено', default=True, db_index=True)
    is_pos = models.BooleanField(u'есть POS-терминал', default=False, db_index=True)
    state = models.BooleanField(u'активно', default=True, db_index=True)

    class Meta:
        verbose_name = u'заведение в kassy.ru'
        verbose_name_plural = u'заведение в kassy.ru'

    def __unicode__(self):
        return self.title


class KassyHall(TicketHall):
    id = models.IntegerField(u'идентификатор', primary_key=True)
    title = models.CharField(u'название', max_length=255)
    descr = models.TextField(u'описание')
    update = models.DateTimeField(u'дата последнего изменения в зале', null=True)
    is_navigated = models.BooleanField(u'отображать по секциям', default=False)
    width = models.IntegerField(u'ширина плана зала', null=True)
    height = models.IntegerField(u'высота плана зала', null=True)
    hidden = models.BooleanField(u'скрыт', default=False, db_index=True)
    state = models.BooleanField(u'активно', default=True, db_index=True)

    building = models.ForeignKey(
        KassyBuilding, on_delete=models.SET_NULL, related_name='halls', verbose_name=u'заведение',
        null=True,
    )

    class Meta:
        verbose_name = u'зал в kassy.ru'
        verbose_name_plural = u'залы в kassy.ru'

    def __unicode__(self):
        return self.title


class KassyEvent(TicketEvent):
    id = models.IntegerField(u'ID', primary_key=True)
    type_id = models.IntegerField(u'id типа зрелища', null=True)
    kassy_rollerman_id = models.IntegerField(u'организатор', null=True, db_index=True)
    title = models.CharField(u'название', max_length=255)
    marginprc = models.IntegerField(u'процент наценки', null=True)
    duration = models.IntegerField(u'продолжительность (сек)', null=True)
    age_restriction = models.CharField(u'возрастное ограничение', max_length=10)
    rating = models.IntegerField(u'рейтинг в баллах', null=True)
    announce = models.TextField(u'описание')
    image = models.URLField(u'адрес изображения')
    is_sale = models.BooleanField(u'продажи разрешены', default=True, db_index=True)
    is_reserv = models.BooleanField(u'бронирование разрешено', default=True, db_index=True)
    state = models.BooleanField(u'активно', default=True, db_index=True)

    objects = TicketEventQuerySet.as_manager()

    class Meta:
        verbose_name = u'событие в kassy.ru'
        verbose_name_plural = u'события в kassy.ru'

    def __unicode__(self):
        return self.title

    @property
    def ticket_label(self):
        return 'kassy'


class KassySession(TicketSession):
    SALE_STATE_ACTIVE = 1
    SALE_STATE_NO_TARIFF = -1
    SALE_STATE_STOP = -2
    SALE_STATE_END = -3

    SALE_STATE_CHOICES = (
        (SALE_STATE_ACTIVE, u'в продаже'),
        (SALE_STATE_NO_TARIFF, u'в продаже, но нет доступа к тарифу'),
        (SALE_STATE_STOP, u'продажа не начата или приостановлена'),
        (SALE_STATE_END, u'продажа завершена'),
    )

    id = models.IntegerField(u'ID', primary_key=True)
    price_min = models.IntegerField(u'минимальная цена', null=True)
    price_max = models.IntegerField(u'максимальная цена', null=True)
    vacancies = models.IntegerField(u'Количество свободных билетов', null=True)
    is_gst = models.BooleanField(u'гастроли', default=True, db_index=False)
    is_prm = models.BooleanField(u'премьера', default=True, db_index=False)
    is_recommend = models.BooleanField(u'рекомендуемое', default=True, db_index=False)
    sale_state = models.IntegerField(
        u'Состояние продаж события', choices=SALE_STATE_CHOICES, default=SALE_STATE_ACTIVE
    )
    state = models.BooleanField(u'активно', default=True, db_index=True)

    event = models.ForeignKey(
        KassyEvent, on_delete=models.SET_NULL, related_name='sessions', verbose_name=u'событие',
        null=True
    )
    hall = models.ForeignKey(
        KassyHall, on_delete=models.SET_NULL, related_name='sessions', verbose_name=u'зал',
        null=True
    )

    class Meta(TicketSession.Meta):
        verbose_name = u'сеанс в kassy.ru'
        verbose_name_plural = u'сеансы в kassy.ru'

    def get_absolute_url(self):
        return u'http://{}.kassy.ru/event/{}'.format(app_settings.KASSY_DB, self.id)


class RamblerBuilding(TicketBuilding):
    id = models.IntegerField(u'ID', primary_key=True)
    name = models.CharField(u'название', max_length=255)
    address = models.CharField(u'адрес', max_length=255)
    latitude = models.FloatField(u'широта')
    longitude = models.FloatField(u'долгота')
    rate = models.CharField(max_length=50)
    category = models.CharField(u'категория', max_length=100)
    sale_from = models.CharField(max_length=50)
    sale_for = models.CharField(max_length=50)
    cancel_type = models.CharField(max_length=100)
    cancel_period = models.IntegerField(null=True)
    is_vvv_enabled = models.BooleanField()
    has_terminal = models.BooleanField(u'есть терминал')
    has_print_device = models.BooleanField(u'есть принтер')
    class_type = models.CharField(u'тип', max_length=30)
    city_id = models.IntegerField(u'id города')

    class Meta:
        verbose_name = u'Заведение Rambler.Kassa'
        verbose_name_plural = u'Заведения Rambler.Kassa'

    def __unicode__(self):
        return self.name


class RamblerHall(TicketHall):
    hallid = models.CharField(u'hall id', max_length=100, db_index=True)
    name = models.CharField(u'название', max_length=255)

    building = models.ForeignKey(
        RamblerBuilding, on_delete=models.SET_NULL, related_name='halls', verbose_name=u'заведение',
        null=True
    )

    class Meta:
        verbose_name = u'Зал в Rambler.Kassa'
        verbose_name_plural = u'Залы в Rambler.Kassa'
        unique_together = ('hallid', 'building')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return u'<RamblerHall {0.id} {0.name}>'.format(self).encode('utf-8')


class RamblerEvent(TicketEvent):
    id = models.IntegerField(u'ID', primary_key=True)
    name = models.CharField(u'название', max_length=255)
    original_name = models.CharField(u'оригинальное название', max_length=255)
    genre = models.CharField(u'жанр', max_length=50)
    country = models.CharField(u'страна', max_length=100)
    view_count_daily = models.IntegerField(null=True)
    age_restriction = models.CharField(u'возрастное ограничение', max_length=5)
    thumbnail = models.CharField(u'миниатюра', max_length=255)
    horizonal_thumbnail = models.CharField(u'горизонтальная миниатюра', max_length=255)
    cast = models.CharField(max_length=1000)
    description = models.CharField(u'описание', max_length=10000)
    director = models.CharField(u'режисер', max_length=1000)
    creator_name = models.CharField(u'производство', max_length=1000)
    creator_id = models.CharField(u'id произовдителя', max_length=5)
    year = models.CharField(u'год', max_length=4)
    duration = models.CharField(u'продолжительность', max_length=10)
    is_non_stop = models.NullBooleanField(default=None)
    rating = models.CharField(u'рейтинг', max_length=10)
    class_type = models.CharField(u'тип', max_length=30)

    objects = TicketEventQuerySet.as_manager()

    class Meta:
        verbose_name = u'Событие в Rambler.Kassa'
        verbose_name_plural = u'События в Rambler.Kassa'

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return u'<RamblerEvent {0.id} {0.name}>'.format(self).encode('utf-8')

    @property
    def ticket_label(self):
        return 'rambler'


class RamblerSession(TicketSession):
    id = models.IntegerField(u'ID', primary_key=True)
    city_id = models.IntegerField(u'id города', null=True)
    creation_class_type = models.CharField(u'тип произведения', max_length=30)
    place_class_type = models.CharField(u'тип места', max_length=30)
    place_id = models.IntegerField(u'id места', null=True, db_index=True)
    format = models.CharField(u'формат', max_length=50)
    is_sale_available = models.BooleanField(u'продажа', default=True)
    is_reservation_available = models.BooleanField(u'бронь', default=True)
    is_without_seats = models.BooleanField(u'без мест', default=False)
    min_price = models.IntegerField(u'мин цена', null=True)
    max_price = models.IntegerField(u'макс цена', null=True)
    hall_name = models.CharField(u'зал', max_length=50)
    fee_type = models.CharField(u'тип сбора', max_length=50)
    fee_value = models.CharField(u'сбор', max_length=10)

    event = models.ForeignKey(
        RamblerEvent, on_delete=models.SET_NULL, null=True, related_name='sessions',
        verbose_name=u'событие'
    )
    hall = models.ForeignKey(
        RamblerHall, on_delete=models.SET_NULL, null=True, related_name='sessions',
        verbose_name=u'зал'
    )

    class Meta(TicketSession.Meta):
        verbose_name = u'Сеанс в Rambler.Kassa'
        verbose_name_plural = u'Сеансы в Rambler.Kassa'


class KinomaxBuilding(TicketBuilding):
    id = models.IntegerField(u'ID', primary_key=True)
    token = models.CharField(u'токен', max_length=255)
    title = models.CharField(u'название', max_length=255)

    class Meta:
        verbose_name = u'заведение в kinomax'
        verbose_name_plural = u'заведения в kinomax'

    def __unicode__(self):
        return self.title


class KinomaxHall(TicketHall):
    title = models.CharField(u'название', max_length=255)

    building = models.ForeignKey(
        KinomaxBuilding, on_delete=models.SET_NULL, related_name='halls', verbose_name=u'заведение',
        null=True
    )

    class Meta:
        verbose_name = u'зал в kinomax'
        verbose_name_plural = u'залы в kinomax'

    def __unicode__(self):
        return self.title


class KinomaxEvent(TicketEvent):
    id = models.IntegerField(u'ID', primary_key=True)
    title = models.CharField(u'название', max_length=255)
    duration = models.IntegerField(u'продолжительность (сек)', null=True)
    rating = models.FloatField(u'рейтинг в баллах', null=True)
    votes = models.IntegerField(u'Количество голосов', null=True)
    description = models.TextField(u'описание')
    director = models.CharField(u'режисер', max_length=255)
    cast = models.CharField(u'актеры', max_length=255)
    trailer = models.URLField(u'трейлер', null=True)
    image = models.URLField(u'адрес изображения', null=True)
    genres = models.CharField(u'название', max_length=255)

    objects = TicketEventQuerySet.as_manager()

    class Meta:
        verbose_name = u'событие в kinomax'
        verbose_name_plural = u'события в kinomax'

    def __unicode__(self):
        return self.title

    @property
    def ticket_label(self):
        return 'kinomax'


class KinomaxSession(TicketSession):
    id = models.IntegerField(u'ID', primary_key=True)
    price = models.CharField(u'название', max_length=255)
    type = models.CharField(u'тип сеанса', max_length=255)
    is_passed = models.BooleanField(u'закончился', default=False, db_index=True)

    event = models.ForeignKey(
        KinomaxEvent, on_delete=models.SET_NULL, related_name='sessions', verbose_name=u'событие',
        null=True
    )
    hall = models.ForeignKey(
        KinomaxHall, on_delete=models.SET_NULL, related_name='sessions', verbose_name=u'зал',
        null=True
    )

    class Meta(TicketSession.Meta):
        verbose_name = u'сеанс в kinomax'
        verbose_name_plural = u'сеансы в kinomax'
