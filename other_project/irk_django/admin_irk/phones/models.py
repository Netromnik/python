# -*- coding: utf-8 -*-

import datetime
import operator
from urlparse import urlparse

import mptt
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed
from django.utils.functional import cached_property

from irk.comments.models import CommentMixin, Comment
from irk.gallery.fields import ManyToGallerysField
from irk.map.models import Cities as City, Streets
from irk.options.models import Site
from irk.phones import managers
from irk.phones.cache import invalidate
from irk.phones.search import FirmSearch, SectionSearch, AddressSearch
from irk.phones.signals import maps_changed, firm_change, firm_post_save, section_post_save
from irk.ratings.models import RateableModel
from irk.utils.fields.file import ImageRemovableField
from irk.utils.helpers import seconds_to_text
from irk.utils.settings import WEEKDAYS, WEEKDAY_MON, WEEKDAY_SUN


def get_content_types():
    return reduce(operator.or_,
                  [Q(app_label=settings.FIRMS_OBJECTS[ct][0], model=settings.FIRMS_OBJECTS[ct][1]) for ct in
                   settings.FIRMS_OBJECTS])


class Ownership(models.Model):
    title = models.CharField(unique=True, max_length=24)
    title_full = models.CharField(blank=True, max_length=255)

    class Meta:
        db_table = u'phones_ownership'
        verbose_name = u'тип'
        verbose_name_plural = u'типы'
        ordering = ['title']

    def __unicode__(self):
        return self.title


class MetaSection(models.Model):
    """Группа категорий телефонного справочника"""

    title = models.CharField(u'Название', max_length=150)
    alias = models.SlugField(u'Алиас')

    class Meta:
        db_table = 'phones_meta_sections'
        verbose_name = u'группа категорий'
        verbose_name_plural = u'группы категорий'

    def __unicode__(self):
        return self.title

    @property
    def slug(self):
        return self.alias


class Sections(models.Model):
    """Рубрики фирм"""

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', db_column='parent',
                               verbose_name='Родительская рубрика')
    name = models.CharField(u'Название', max_length=255)
    name_short = models.CharField(u'Короткое название', max_length=255, blank=True)
    slug = models.SlugField(u'Алиас', null=True, blank=True, unique=True)
    css_class = models.SlugField(u'СSS класс', null=True, blank=True)
    position = models.SmallIntegerField(u'Позиция', null=True, blank=True)
    views = models.IntegerField(editable=False, default=0)
    org_count = models.IntegerField(editable=False, default=0)
    new_org_count = models.IntegerField(editable=False, default=0)
    logo = ImageRemovableField(upload_to='img/site/phones/sections_logo/', blank=True, verbose_name=u'Логотип')
    is_guide = models.BooleanField(u'Гид по городу', db_index=True, default=False)
    content_type = models.ForeignKey(ContentType, blank=True, null=True, verbose_name=u'Тип')
    on_guide_index = models.BooleanField(u'Выводить по умолчанию для гида', db_index=True, default=False)
    in_map = models.BooleanField(u'Выводить в путеводителе карты', default=False, blank=True, db_index=True)
    in_mobile = models.BooleanField(u'Выводить в мобильных местах отдыха', default=False, blank=True, db_index=True)
    sites = models.ManyToManyField(Site, blank=True, verbose_name=u'Разделы')
    categories = models.ManyToManyField(MetaSection, blank=True, verbose_name=u'Категории')
    place_logo = ImageRemovableField(verbose_name=u'Логотип мобильных мест', upload_to='img/site/phones/place_logo/', blank=True, null=True)
    #  min_size=(60, 60), max_size=(100, 100)

    objects = managers.Section()

    search = SectionSearch()

    obed_id = models.IntegerField(blank=True)

    class Meta:
        db_table = u'phones_sections'
        verbose_name = u'рубрику'
        verbose_name_plural = u'рубрики'
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        parent_in_db = False
        up_level = False

        if self.level == 0:
            self.level = 1
            up_level = True

        if self.pk and self.parent and not self.parent.get_descendants().filter(pk=self.pk).count():
            # Т.е у рубрики изменился родитель
            parent_in_db = Sections.objects.get(pk=self.pk).parent

        obj = super(Sections, self).save(*args, **kwargs)

        if up_level:
            for section in self.get_descendants(include_self=False):
                section.level = section.level + 1
                section.save()

        if parent_in_db:
            parent_in_db.recalculate_firms_count()

        if self.on_guide_index:
            if self.pk:
                qs = Sections.objects.exclude(pk=self.pk)
            else:
                qs = Sections.objects.all()
            qs.update(on_guide_index=False)

        return obj

    def recalculate_firms_count(self):
        """Пересчет счетчика количества фирм у этой рубрики и ее родителей"""

        self.org_count = Firms.objects.filter(section__in=self.get_descendants(include_self=True), visible=True).count()

        # Ultra-fast atomic database update
        Sections.objects.filter(pk=self.pk).update(org_count=self.org_count)

        for section in self.get_ancestors():
            Sections.objects.filter(pk=section.pk).update(org_count=Firms.objects.filter(visible=True,
                                                                                         section__in=section.get_descendants(
                                                                                             include_self=True)).count())

    @models.permalink
    def get_absolute_url(self):
        if self.rght - self.lft == 1:
            return ('map.views.firms_list', (), {'rubric_id': self.pk})
        else:
            return ('rubric', (), {'id': self.pk})

    def has_firms(self):
        if self.level == 3:
            return True
        elif self.level == 2:
            return Firms.objects.filter(section=self, visible=True).count() > 0
        return False

    def __getattr__(self, attr):
        attr_data = attr.split("_")
        if attr_data.pop() == "firms":
            try:
                content_type = ContentType.objects.get(model=attr_data[0])
                return self.firms_set.filter(content_type=content_type).order_by("name")
            except:
                pass
        return super(Sections, self).__getattr__(attr)


try:
    mptt.register(Sections, )
except:
    pass

post_save.connect(invalidate, sender=Sections)


class Firms(CommentMixin, RateableModel, models.Model):
    maps = None
    visblity_changed = False

    section = models.ManyToManyField(Sections, verbose_name=u'Рубрика', blank=True)
    user = models.ForeignKey(User, null=True, blank=True, verbose_name=u'Пользователь')
    apteka_id = models.IntegerField(null=True, blank=True, editable=False)  # TODO не используется
    name = models.CharField(max_length=255, verbose_name=u'Название')
    alternative_name = models.CharField(verbose_name=u'Альтернативное название', max_length=255, blank=True)
    ownership = models.ForeignKey(Ownership, db_column='ownership', verbose_name=u'Форма собственности', blank=True,
                                  null=True)  # TODO не используется
    url = models.CharField(max_length=255, verbose_name=u'Веб-сайт', blank=True)
    mail = models.EmailField(verbose_name=u'E-mail', blank=True)
    skype = models.CharField(max_length=100, verbose_name=u'Skype', blank=True,
                             null=True)  # TODO используется только в туризме
    description = models.TextField(blank=True, verbose_name=u'Описание')
    updated = models.DateTimeField(auto_now=True, editable=False)
    pay_info_until = models.DateTimeField(null=True, blank=True, editable=False)  # TODO не используется
    pay_top_until = models.DateTimeField(null=True, blank=True, editable=False)  # TODO не используется
    visible = models.BooleanField(default=False, verbose_name=u'Показывать', db_index=True)
    views = models.IntegerField(editable=False, default=0)
    changed = models.BooleanField(editable=False, default=False)
    comments_cnt = models.IntegerField(editable=False, default=0)
    last_comment_id = models.IntegerField(null=True, editable=False)
    logo = ImageRemovableField(upload_to='img/site/phones/logo/', blank=True, null=True, verbose_name=u'Логотип') # max_size=(1024, 768)
    map_logo = ImageRemovableField(upload_to='img/site/phones/logo/map/', blank=True, null=True, verbose_name=u'Логотип на карте',
                     help_text=u'Размер: 90x50 пикселей')  # TODO не используется  max_size=(90, 50)
    app_comment = models.TextField(blank=True, verbose_name=u'Комментарий')  # TODO не используется
    content_type = models.ForeignKey(ContentType, blank=True, null=True, verbose_name=u'Тип',
                                     limit_choices_to=get_content_types())
    gis_id = models.IntegerField(null=True, editable=False)  # TODO не используется
    wide_image = ImageRemovableField(verbose_name=u'Широкоформатная фотография', upload_to='img/site/phones/wide/',
                       blank=True, null=True)

    gallery = ManyToGallerysField()

    search = FirmSearch()

    class Meta:
        db_table = u'phones_firms'
        ordering = ['name']
        verbose_name = u'организацию'
        verbose_name_plural = u'организации'

    def get_absolute_url(self):
        try:
            descendant = next(self.descendants())
            return descendant.get_absolute_url()
        except StopIteration:
            return ''

    def get_url(self):
        if not self.url.startswith(('http://', 'https://', '//',)):
            self.url = 'http://%s' % self.url
        url = urlparse(self.url, scheme='http')
        return url.geturl()

    def get_email(self):
        email = self.mail
        email = email.split("@")
        code = 'var loy = "%s"; loy = "%s" + "@" + loy; document.write(\'<a href="mailto:\' + loy + \'">\' + loy + \'</a>\');' % (
            email[1], email[0])
        return code

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                in_db = Firms.objects.get(pk=self.pk)
                if self.visible != in_db.visible:
                    self.visblity_changed = True
            except Firms.DoesNotExist:
                pass

        super(Firms, self).save(*args, **kwargs)

    def descendants(self):
        """Итератор, возвращающий модели-наследники данной фирмы

        Делает `len(phones.firms_library)` запросов в БД
        """

        from irk.phones.helpers import firms_library

        for cls in firms_library:
            try:
                yield cls.objects.get(firms_ptr_id=self.id)
            except cls.DoesNotExist:
                continue

    @cached_property
    def main_address(self):
        """Основной адрес фирмы"""
        try:
            main_address = Address.objects.filter(firm_id=self, is_main=True) \
                .prefetch_related('address_worktimes').select_related('city_id')[0]
        except IndexError:
            try:
                main_address = Address.objects.filter(firm_id=self) \
                    .prefetch_related('address_worktimes').select_related('city_id')[0]
            except IndexError:
                main_address = None

        return main_address

    @cached_property
    def other_addresses(self):
        """Остальные адреса фирмы"""

        addresses = Address.objects.filter(firm_id=self).prefetch_related('address_worktimes').select_related('city_id')
        if self.main_address:
            addresses = addresses.exclude(pk=self.main_address.pk)

        return addresses


m2m_changed.connect(maps_changed, sender=Firms.section.through)
post_save.connect(firm_post_save, sender=Firms)
post_save.connect(section_post_save, sender=Sections)
m2m_changed.connect(firm_change, sender=Firms.section.through)


class SectionFirm(Firms):
    """Абстрактный базовый класс для всех моделей компаний в других разделах

    Если фирму «удалили» из рубрики, отвечающей за вывод фирм в разделе, ``is_active`` равен False,
    и фирма никогда не выводится в этом разделе

    Внимание! При изменении полей этой модели помните, что необходимо будет сделать миграции во всех разделах,
    где она используется
    """

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(SectionFirm, self).save(*args, **kwargs)

        post_save.send(sender=self._meta.concrete_model, instance=self, created=False)


post_save.connect(invalidate, sender=Firms)


class Address(models.Model):
    # TODO переименовать firm_id в firm
    firm_id = models.ForeignKey(Firms, db_column='firm_id')
    # TODO переименовать city_id в city
    city_id = models.ForeignKey(City, db_column='city_id', verbose_name=u'Город', default=1)
    name = models.CharField(u'Aдрес', max_length=255, blank=True)
    location = models.CharField(max_length=255, verbose_name=u'Дом', blank=True)
    officenumber = models.CharField(max_length=30, db_column='officeNumber', verbose_name=u'Офис', blank=True)
    descr = models.CharField(max_length=255, verbose_name=u'Доп. описание', blank=True,
        help_text=u'Уточнение для поиска нужного здания, например: «ост. Микрохирургия глаза, здание Энергоколледжа»')
    streetid = models.ForeignKey(Streets, null=True, db_column='streetID', blank=True, )
    streetname = models.CharField(max_length=255, db_column='streetName', verbose_name=u'Улица', blank=True)
    is_main = models.BooleanField(u'Основной адрес', default=False)
    priority = models.IntegerField(editable=False, default=0)
    phones = models.CharField(max_length=255, verbose_name=u'Телефоны', blank=True, null=True)
    twenty_four_hour = models.BooleanField(u'Круглосуточно', default=False)
    worktime = models.CharField(max_length=255, blank=True, verbose_name=u'Часы работы')
    map = ImageRemovableField(upload_to='img/site/phones/maps/', blank=True, verbose_name=u'Карта проезда')
    map_logo = models.BooleanField(default=False, verbose_name=u'Выводить логотип на карте')
    point = models.PointField(u'Геокоординаты', spatial_index=False, null=True, blank=True)

    search = AddressSearch()

    objects = models.GeoManager()

    class Meta:
        db_table = u'phones_address'
        verbose_name = u'адрес'
        verbose_name_plural = u'адреса'

    def __init__(self, *args, **kwargs):
        super(Address, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = ",".join(
                [unicode(self.city_id), unicode(self.streetid), unicode(self.location), unicode(self.officenumber)])
            if not self.streetname and self.streetid:
                self.streetname = self.streetid.name

        super(Address, self).save(*args, **kwargs)

    @cached_property
    def worktime_order(self):
        """
        Свойство для сортировки адресов по времени открытия и закрытия с учетом обеденного времени.
        Возвращает число секунд до закрытия. Если адрес закрыт то отрицательное число секунд до открытия.
        Если адрес работает круглосуточно, то возвращает максимально возможное число (количество секунд в неделе).
        Если адрес не имеет связанных объектов "время работы", возвращается None.

        :return: Возвращает число секунд до закрытия или открытия.
        :rtype: int or None
        """

        if self.twenty_four_hour:
            return 60 * 60 * 24 * 7

        if not self.has_worktime:
            return None

        dtime = datetime.datetime.now()
        stamp = dtime.weekday() * 60 * 60 * 24 + dtime.hour * 60 * 60 + dtime.minute * 60

        current_worktime = self.current_worktime
        if current_worktime:
            if current_worktime.dinner_start_stamp > stamp:
                return current_worktime.dinner_start_stamp - stamp
            else:
                return current_worktime.end_stamp - stamp
        else:
            # Не работает в обеденное время
            worktime = self.address_worktimes.filter(dinner_start_stamp__lte=stamp, dinner_end_stamp__gt=stamp).first()
            if worktime:
                return stamp - worktime.dinner_end_stamp
            else:
                # Не работает в нерабочее время
                worktime = self.address_worktimes.filter(start_stamp__gt=stamp).order_by('start_stamp').first()
                if not worktime:
                    worktime = self.address_worktimes.all().order_by('start_stamp').first()
                    stamp -= 60 * 60 * 24 * 7
                return stamp - worktime.start_stamp

    @cached_property
    def current_worktime(self):
        """
        Если заведение в текущее время работает то возвращается объект Worktime текущего рабочего дня.
        Например для заведения с временем работы ПН-ПТ 07:00 - 01:00 в СБ 00:30 вернет объект ПТ.

        :return: Объект времени работы текущего дня или ничего
        :rtype: Worktime or None
        """

        if self.twenty_four_hour:
            return None

        dtime = datetime.datetime.now()
        stamp = dtime.weekday() * 60 * 60 * 24 + dtime.hour * 60 * 60 + dtime.minute * 60

        try:
            current_worktime = self.address_worktimes.filter(start_stamp__lte=stamp, end_stamp__gt=stamp) \
                .exclude(dinner_start_stamp__lte=stamp, dinner_end_stamp__gt=stamp)[0]
        except IndexError:
            current_worktime = None
        if not current_worktime and dtime.weekday() == WEEKDAY_MON:
            end_week_stamp = stamp + 60 * 60 * 24 * 7  # Количество секунд в неделе
            # Если у заведения время работы в ВС больше 00:00 то количество секунд в штампе окончания работы в ВС
            # больше числа секунд в неделе. Поэтому в ПН мы получаем число секунд от начала недели, прибовляем
            # количество секунд в неделе и сравниваем штамп окончания работы в ВС с этим значением.
            current_worktime = self.address_worktimes.filter(weekday=WEEKDAY_SUN,
                                                             end_stamp__gte=end_week_stamp + stamp).first()

        return current_worktime

    @cached_property
    def open_everyday_at_same_time(self):
        """Работает каждый день в одно и тоже время"""

        if self.twenty_four_hour:
            return True

        worktimes = self.address_worktimes.all()
        if not worktimes:
            return False

        # Открыто каждый день
        if not {worktime.weekday for worktime in worktimes} == set(WEEKDAYS.keys()):
            return False

        # В одно и тоже время работает и обедает
        start_time = worktimes[0].start_time
        end_time = worktimes[0].end_time
        dinner_start_time = worktimes[0].dinner_start_time
        dinner_end_time = worktimes[0].dinner_end_time
        for worktime in worktimes:
            if worktime.start_time != start_time or worktime.end_time != end_time:
                return False
            if worktime.dinner_start_time != dinner_start_time or worktime.dinner_end_time != dinner_end_time:
                return False

        return True

    @cached_property
    def has_worktime(self):
        """Есть ли рабочее время"""

        return self.address_worktimes.exists()

    @cached_property
    def has_dinner(self):
        """Есть ли обед у в какой-либо день"""

        if self.twenty_four_hour or not self.has_worktime:
            return False

        worktimes = self.address_worktimes.all()
        for worktime in worktimes:
            if worktime.has_dinner:
                return True
        return False

    @cached_property
    def dinner_everyday_at_same_time(self):
        """Обед каждый день в одно и тоже время"""

        if self.twenty_four_hour:
            return False

        worktimes = self.address_worktimes.all()
        if not worktimes:
            return False

        # В одно и тоже время
        dinner_start_time = worktimes[0].dinner_start_time
        dinner_end_time = worktimes[0].dinner_end_time
        for worktime in worktimes:
            if worktime.dinner_start_time != dinner_start_time or worktime.dinner_end_time != dinner_end_time:
                return False

        return {
            'dinner_start_time': dinner_start_time,
            'dinner_end_time': dinner_end_time,
        }

    @cached_property
    def address_with_city(self):
        """
        Возвращает адрес из поля name и добавляет название города если это не Иркутск

        :return: Адрес
        :rtype: str
        """
        if not self.city_id or self.city_id.alias == 'irkutsk':
            return self.name
        else:
            return u'{}, {}'.format(self.city_id.name, self.name)

    @cached_property
    def closing_in_3_hours(self):
        """
        Выводит время до закрытия заведения в виде текста если оно закрывается в течении ближайших 3х часов
        """

        if self.twenty_four_hour or not self.has_worktime:
            return None

        dtime = datetime.datetime.now()
        stamp = dtime.weekday() * 60 * 60 * 24 + dtime.hour * 60 * 60 + dtime.minute * 60

        result = None

        current_worktime = self.current_worktime
        if current_worktime:

            if dtime.weekday() == WEEKDAY_MON and current_worktime.end_stamp > 60 * 60 * 24 * 7:
                stamp += 60 * 60 * 24 * 7
            if current_worktime.end_stamp - 60 * 60 * 3 < stamp:
                result = u'открыт еще {}'.format(seconds_to_text(current_worktime.end_stamp - stamp, end=4))
            elif current_worktime.dinner_start_stamp - 60 * 60 <= stamp < current_worktime.dinner_end_stamp:
                result = u'закроется на обед через {}'.format(
                    seconds_to_text(current_worktime.dinner_start_stamp - stamp, end=4))

        return result

    @cached_property
    def open_in(self):
        """
        Выводит время до открытия заведения в виде текста
        """

        if self.twenty_four_hour or not self.has_worktime:
            return None

        dtime = datetime.datetime.now()
        stamp = dtime.weekday() * 60 * 60 * 24 + dtime.hour * 60 * 60 + dtime.minute * 60

        result = None
        if not self.current_worktime:
            # Не работает в обеденное время
            worktime = self.address_worktimes.filter(dinner_start_stamp__lte=stamp, dinner_end_stamp__gt=stamp).first()
            if worktime:
                stamp_diff = worktime.dinner_end_stamp - stamp
            else:
                # Не работает в нерабочее время
                worktime = self.address_worktimes.filter(start_stamp__gt=stamp).order_by('start_stamp').first()
                if not worktime:
                    worktime = self.address_worktimes.all().order_by('start_stamp').first()
                    stamp -= 60 * 60 * 24 * 7
                stamp_diff = worktime.start_stamp - stamp

            # Выводить минуты только если осталось 3 часа до отрытия
            if stamp_diff < 3 * 60 * 60:
                result = seconds_to_text(stamp_diff, end=4)
            else:
                result = seconds_to_text(stamp_diff, end=4, length=1)

            result = u'откроется через {}'.format(result)

        return result

    @property
    def building_address(self):
        chunks = []
        if self.city_id:
            chunks.append(unicode(self.city_id))
        if self.streetid:
            chunks.append(unicode(self.streetid))
        if not self.streetid and self.streetname:
            chunks.append(self.streetname)
        if self.location:
            chunks.append(unicode(self.location))
        if self.officenumber:
            chunks.append(self.officenumber)
        return u', '.join(chunks)

    def __unicode__(self):
        return self.building_address

    def get_absolute_url(self):
        return "/phones/address/" + str(self.pk) + "/"

    # TODO: проверить на пригодность.
    def get_geo(self):
        ''' Возвращает координаты центра объекта '''

    geo = property(get_geo)

    def is_full(self):
        """Имеет все данные, чтобы можно было точно определить дом"""

        return self.city_id and (self.streetid or self.streetname) and self.location


post_save.connect(invalidate, sender=Address)


class Worktime(models.Model):
    """Время работы"""

    WEEKDAY_CHOICES = WEEKDAYS.items()

    address = models.ForeignKey(Address, verbose_name=u'Адрес', related_name=u'address_worktimes')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name=u"День недели")
    start_time = models.TimeField(u'Время начала работы')
    end_time = models.TimeField(u'Время окончания работы')
    dinner_start_time = models.TimeField(u'Время начала обеда', null=True, blank=True)
    dinner_end_time = models.TimeField(u'Время окончания обеда', null=True, blank=True)
    start_stamp = models.IntegerField(u'Время начала работы в секундах')
    end_stamp = models.IntegerField(u'Время окончания работы в секундах')
    dinner_start_stamp = models.IntegerField(u'Время начала обеда в секундах', null=True, blank=True)
    dinner_end_stamp = models.IntegerField(u'Время окончания обеда в секундах', null=True, blank=True)

    class Meta:
        verbose_name = u'время работы'
        verbose_name_plural = u'время работы'
        unique_together = ('address', 'weekday')

    def save(self, *args, **kwargs):
        # Высчитываем число секунд с начала недели
        self.start_stamp = self.weekday * 60 * 60 * 24 + self.start_time.hour * 60 * 60 + self.start_time.minute * 60
        self.end_stamp = self.weekday * 60 * 60 * 24 + self.end_time.hour * 60 * 60 + self.end_time.minute * 60
        # Если время окончания работы больше 23.59 то оно меньше времени начала работы. Поэтому добавляем количество
        # секунд в сутках к штампу окончания работы, чтобы оно было больше штампа начала работ.
        if self.start_time >= self.end_time:
            self.end_stamp += 60 * 60 * 24
        # Высчитываем число секунд с начала недели для обеда

        if self.dinner_start_time and self.dinner_end_time:
            self.dinner_start_stamp = self.weekday * 60 * 60 * 24 + self.dinner_start_time.hour * 60 * 60 \
                                      + self.dinner_start_time.minute * 60
            self.dinner_end_stamp = self.weekday * 60 * 60 * 24 + self.dinner_end_time.hour * 60 * 60 \
                                    + self.dinner_end_time.minute * 60
        else:
            self.dinner_start_stamp = None
            self.dinner_end_time = None
        super(Worktime, self).save(*args, **kwargs)

    @property
    def has_dinner(self):
        return self.dinner_start_time and self.dinner_end_time

    @property
    def now_work(self):
        """Сейчас работает"""

        stamp = self._get_now_stamp()

        return (self.start_stamp <= stamp < self.end_stamp) and not self.now_dinner

    @property
    def now_dinner(self):
        """Сейчас обед"""

        if not self.has_dinner:
            return False

        stamp = self._get_now_stamp()

        return self.dinner_start_stamp <= stamp < self.dinner_end_stamp

    @staticmethod
    def _get_now_stamp():
        """
        Вернуть метку текущего времени. Представляет собой количество секунд с начала недели.
        Используется для сравнения меток начала/конца работы с текущим моментом вермени.

        :return: метка текущего времени.
        :rtype: int
        """

        now = datetime.datetime.now()

        return now.weekday() * 60 * 60 * 24 + now.hour * 60 * 60 + now.minute * 60

    def __unicode__(self):
        return u'{0} {1.start_time:%H:%M} - {1.end_time:%H:%M}'.format(self.get_weekday_display(), self)
