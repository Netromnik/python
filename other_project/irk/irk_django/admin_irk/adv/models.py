import datetime
import os
import random
import time
import urllib

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import signals
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.html import escape, mark_safe

from about.models import Price
from adv.settings import BANNER_ROOT
from adv.signals import period_post_save, extract_html5_banner
from adv.validators import validate_banner_file_extension, validate_html5_file
from invoice.models import BaseOrder
from options.models import Site
from utils.db.models.fields import ColorField
from utils.fields.file import FileRemovableField, ImageRemovableField, FileArchiveField
from utils.fields.onetoone import AutoOneToOneField
from utils.validators import FileSizeValidator


class Place(models.Model):
    """Место размещения баннеров"""

    position = models.PositiveIntegerField('Позиция', default=0)
    name = models.CharField('Название', max_length=255)
    show_text = models.BooleanField('Показывать текст под баннером', default=False)
    visible = models.BooleanField('Существующее место', default=True)
    dayPrice = models.FloatField(u"Цена за день размещения", default=0.0)
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=u"Раздел сайта")
    about_price = models.OneToOneField(Price, verbose_name=u"Прайс", blank=True, null=True, related_name="adv_place",
                                       on_delete=models.CASCADE)
    booking_visible = models.BooleanField('Выводить в бронировании', default=True)
    empty_notif = models.BooleanField('Уведомлять о простое', default=False)
    targetix = models.ForeignKey('adv.Targetix', null=True, blank=True, verbose_name='Внешний баннер',
                                 related_name='places', on_delete=models.CASCADE)
    targetix2 = models.ForeignKey('adv.Targetix', null=True, blank=True, verbose_name='Внешний баннер 2',
                                  related_name='places2', help_text='Показывается 50/50 с внешним баннером 1',
                                  on_delete=models.CASCADE)
    juridical_required = models.BooleanField('Требовать юридическое название клиента', default=False,
                                             help_text='Доп. информация о клиенте, выводящаяся на сайте')

    class Meta:
        verbose_name = 'место размещения'
        verbose_name_plural = 'места размещения'

    def __str__(self):
        return self.name


class Template(models.Model):
    name = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ClientType(models.Model):
    """Тип организации"""

    type = models.CharField(verbose_name=u"Тип", max_length=255)

    class Meta:
        verbose_name = 'тип организации'
        verbose_name_plural = 'типы организаций'

    def __str__(self):
        return self.type


class Client(models.Model):
    """Клиент"""

    OWNERSHIP = (
        ('ООО', 'ООО'),
        ('ЗАО', 'ЗАО'),
        ('ОАО', 'ОАО'),
        ('НОУДО', 'НОУДО'),
        ('ИП', 'ИП'),
        ('ЧП', 'ЧП'),
    )
    name = models.CharField('Имя', max_length=255)
    juridical_name = models.CharField('Юридическое название', max_length=255, blank=True, null=True)
    address = models.TextField(verbose_name=u"Адрес доставки", blank=True, null=True)
    type = models.ForeignKey(ClientType, verbose_name=u"Тип", null=True, blank=True, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, verbose_name=u"Менеджер", null=True, blank=True, on_delete=models.CASCADE)
    ownership = models.CharField(verbose_name=u"Форма собственности", choices=OWNERSHIP, max_length=7, default='ООО')
    info = models.TextField(verbose_name=u"Дополнительная информация", blank=True, default='')
    is_deleted = models.BooleanField(verbose_name=u"Удален", default=False, db_index=True)
    is_active = models.BooleanField(verbose_name=u"Не в черном списке", default=True, db_index=True)
    cause = models.TextField(verbose_name=u"Причина занесения в черный список", blank=True, default='')

    class Meta:
        permissions = (("can_reassign_manager", "Can reassign manager"),)
        verbose_name = 'клиента'
        verbose_name_plural = 'клиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Contact(models.Model):
    """Контактное лицо"""

    name = models.CharField(u"ФИО", max_length=200, blank=True)
    email = models.EmailField(u"Электронная почта", max_length=100, blank=True)
    phone = models.CharField(u"Телефон", max_length=100, blank=True, null=True)
    primary_contact = models.BooleanField(u"Основной контакт?", default=False)
    client = models.ForeignKey(Client, verbose_name=u"Клиент", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'контакт'
        verbose_name_plural = 'контакты'

    def __str__(self):
        return self.name


class Booking(models.Model):
    """Бронь"""

    client = models.ForeignKey(Client, verbose_name=u"Клиент", on_delete=models.CASCADE)
    place = models.ForeignKey(Place, verbose_name=u"Место размещения", on_delete=models.CASCADE)
    from_date = models.DateField(u"Дата начала")
    to_date = models.DateField(u"Дата окончания")
    finalPrice = models.FloatField(u"Стоимость со скидкой", blank=True, default=0, null=True)
    comment = models.TextField(u"Примечание", blank=True)
    payed = models.BooleanField(u"Оплачено", default=False)
    cash = models.BooleanField(u"Наличными", default=False)
    deleted = models.BooleanField(u"Удалено", default=False)
    sale = models.FloatField(u"Скидка в процентах", blank=True, default=0, null=True)
    price = models.FloatField(u"Стоимость", blank=True, default=0, null=True)

    class Meta:
        permissions = (
            ("can_generate_reports", "Can generate reports"),
            ("can_edit_old_bookings", "Can edit old bookings"),
            ("can_edit_not_own_bookings", "Can edit not own bookings"),
            ("can_use_bookings_system", "Can use booking system"),
        )
        verbose_name = 'бронирование'
        verbose_name_plural = 'бронирования'

    def __str__(self):
        try:
            return '%s - %s - %s' % (self.client.name, self.place.site.name, self.place.name)
        except Site.DoesNotExist:
            return '%s - %s' % (self.client.name, self.place.name)


class Payment(models.Model):
    """Оплата брони"""

    amount = models.FloatField(u"Сумма платежа", default=0)
    date = models.DateField(u"Дата платежа", default=datetime.date.today)
    booking = models.ForeignKey(Booking, verbose_name=u"Бронь", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'оплата'
        verbose_name_plural = 'оплата'


class Action(models.Model):
    action = models.CharField(u"Название действия", max_length=50)

    class Meta:
        verbose_name = 'действие'
        verbose_name_plural = 'действия'

    def __str__(self):
        return self.action


class BookingHistory(models.Model):
    user = models.ForeignKey(User, verbose_name=u"Пользователь", on_delete=models.CASCADE)
    action = models.ForeignKey(Action, verbose_name=u"Действие над бронью", on_delete=models.CASCADE)
    date_of_action = models.DateTimeField(u"Дата и время", default=datetime.datetime.now)
    booking = models.ForeignKey(Booking, verbose_name=u"Бронирование", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'лог бронирования'
        verbose_name_plural = 'лог бронирования'

    def __str__(self):
        try:
            return '%s - %s - %s - %s' % (self.user.username, self.action.action,
                                          self.booking.place.site.name, self.booking.place.name)
        except Site.DoesNotExist:
            return '%s - %s - %s' % (self.user.username, self.action.action, self.booking.place.name)


class TypeOfCommunication(models.Model):
    type = models.CharField(verbose_name=u"Тип коммуникации", max_length=100)

    class Meta:
        verbose_name = 'тип коммуникации'
        verbose_name_plural = 'типы коммуникаций'

    def __str__(self):
        return self.type


class ManagerClientHistory(models.Model):
    user = models.ForeignKey(User, verbose_name=u"Пользователь", null=True, default=None, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, verbose_name=u"Действие над клиентом", on_delete=models.CASCADE)
    date_of_action = models.DateTimeField(u"Дата и время", default=datetime.datetime.now)
    client = models.ForeignKey(Client, verbose_name=u"Клиент", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'лог работы с клиеном'
        verbose_name_plural = 'лог работы с клиенами'

    def __str__(self):
        return '%s - %s - %s' % (self.user.username, self.action.action, self.client.name)


class MailHistory(models.Model):
    manager = models.ForeignKey(User, verbose_name=u"Пользователь", on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Contact, verbose_name=u"Получатели", through='MailHistory_Recipients')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u"Дата и время отправки")
    title = models.CharField(max_length=500, verbose_name=u"Тема")
    text = models.TextField(verbose_name=u"Текст")

    class Meta:
        verbose_name = 'почтовая рассылка'
        verbose_name_plural = 'почтовые рассылки'

    def __str__(self):
        return '%s - %s' % (self.title, self.date.strftime("%d.%m.%Y %H:%M:%S"))


class Communication(models.Model):
    date = models.DateField(verbose_name=u"Дата коммуникации", default=datetime.datetime.now, blank=True, null=True)
    time = models.TimeField(verbose_name=u"Время коммуникации", null=True, blank=True, default=None)
    type = models.ForeignKey(TypeOfCommunication, verbose_name=u"Тип коммуникации", on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name=u"Клиент", on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, verbose_name=u"Контактное лицо", blank=True, null=True,
                                on_delete=models.CASCADE)
    manager = models.ForeignKey(User, verbose_name=u"Менеджер", on_delete=models.CASCADE)
    result = models.TextField(blank=True, null=True, default='', verbose_name=u"Результат")
    target = models.TextField(blank=True, null=True, default='', max_length=100, verbose_name=u"Примечание")
    is_deleted = models.BooleanField(default=False, verbose_name=u"Удалена")
    is_done = models.BooleanField(default=False, verbose_name=u"Завершена")
    mail_msg = models.ForeignKey(MailHistory, blank=True, null=True, verbose_name=u"Письмо", on_delete=models.CASCADE)
    notify_time = models.TimeField(verbose_name=u"Время напоминания до события", blank=True, null=True, default=None)
    next_communication = models.DateField(blank=True, verbose_name=u"Дата следующей коммуникации", null=True,
                                          default=None)  # TODO унаследовано от старой ЦРМ для сохранения совместимости. Со временем надобность в нем отпадет. Не забыть поправить функциюю communications.duties
    booking = models.ForeignKey(Booking, verbose_name=u"Бронирование", default=None, blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'коммуникация'
        verbose_name_plural = 'коммуникации'

    def __str__(self):
        if self.date:
            return '%s - %s - %s' % (self.client.name, self.date.strftime('%d.%m.%Y'), self.type.type)
        else:
            return '%s - %s' % (self.client.name, self.type.type)


class CommunicationHistory(models.Model):
    user = models.ForeignKey(User, verbose_name=u"Пользователь", on_delete=models.CASCADE)
    action = models.ForeignKey(Action, verbose_name=u"Действие над коммуникацией", on_delete=models.CASCADE)
    date_of_action = models.DateTimeField(u"Дата и время", default=datetime.datetime.now)
    communication = models.ForeignKey(Communication, verbose_name=u"Коммуникация", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'лог коммуникации'
        verbose_name_plural = 'лог коммуникаций'

    def __str__(self):
        return '%s - %s - %s' % (self.user.username, self.action.action, self.communication.client.name)


class SMTPErrors(models.Model):
    SMTP_ERROR_TYPE = (
        ('2XX', 'Команда успешно выполнена'),
        ('3XX', 'Ожидаются дополнительные данные от клиента'),
        ('4XX', 'Временная ошибка, клиент должен произвести следующую попытку через некоторое время'),
        ('5XX', 'Неустранимая ошибка'),
    )
    code = models.PositiveIntegerField(primary_key=True, verbose_name=u"Код ошибки")
    definition = models.TextField(default='', verbose_name=u"Описание")
    type = models.CharField(max_length=255, choices=SMTP_ERROR_TYPE, null=True, verbose_name=u"Тип")

    class Meta:
        verbose_name = 'ошибка SMTP сервера'
        verbose_name_plural = 'ошибки SMTP сервера'

    def __str__(self):
        return '%d - %s' % (self.code, self.definition)


class MailHistory_Recipients(models.Model):
    mailhistory = models.ForeignKey(MailHistory, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    error_code = models.ForeignKey(SMTPErrors, default=None, null=True, blank=True, on_delete=models.CASCADE)
    is_sent = models.NullBooleanField(default=False, null=True, blank=True)

    class Meta:
        verbose_name = 'рассылка по контактам'
        verbose_name_plural = 'рассылки по контактам'

    def __str__(self):
        return '%s - %s'.format(self.mailhistory.date.strftime("%d.%m.%Y %H:%M:%S"), self.contact.name)


def random_color():
    reds = random.uniform(10, 255)
    greens = random.uniform(10, 255)
    blues = random.uniform(10, 255)
    return '#%x' % reds + '%x' % greens + '%x' % blues


class UserOption(models.Model):
    user = AutoOneToOneField(User, verbose_name=u"Пользователь", primary_key=True, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, default=random_color, blank=True, null=True, verbose_name=u"Цвет")
    show_done_duties = models.BooleanField(verbose_name=u"Показывать выполненные дела", default=True)

    class Meta:
        verbose_name = 'настройка пользователей CRM'
        verbose_name_plural = 'настройки пользователей CRM'

    def __str__(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username


class Banner(models.Model):
    """Баннер"""

    ROLL_TOP = 1
    ROLL_RIGHT = 2
    ROLL_BOTTOM = 3
    ROLL_LEFT = 4
    ROLL_CHOICES = (
        (ROLL_LEFT, 'Налево'),
        (ROLL_RIGHT, 'Направо'),
    )

    name = models.CharField('Название', max_length=255)
    client = models.ForeignKey(Client, verbose_name='Клиент',on_delete=models.CASCADE)
    url = models.CharField('Ссылка', max_length=255, blank=True, null=True)
    alt = models.CharField('Alt', max_length=255, blank=True, null=True)
    bgcolor = ColorField('Цвет фона', blank=True, null=True)
    pixel_audit = models.CharField('Код для пиксель-аудита', max_length=255, blank=True)
    places = models.ManyToManyField(Place, related_name='banners', verbose_name='Места размещения')
    show_time_start = models.TimeField(verbose_name='Время показа с', blank=True, null=True)
    show_time_end = models.TimeField(verbose_name='Время показа по', blank=True, null=True)
    width = models.PositiveSmallIntegerField('ширина', blank=True, null=True)
    height = models.PositiveSmallIntegerField('высота', blank=True, null=True)
    roll_direction = models.PositiveSmallIntegerField('Направление разворота', choices=ROLL_CHOICES, blank=True,
                                                      null=True)
    roll_width = models.PositiveSmallIntegerField('Ширина баннера в свернутом состоянии', blank=True, null=True,
                                                  help_text='Указывается в пикселях')
    invoice = models.CharField('Номер счета', max_length=100, default='', blank=True)
    is_payed = models.BooleanField('Счет оплачен', default=False)
    is_alternate_external = models.BooleanField('Чередовать с внешним баннером', default=False)

    # Временные поля для оперативного подсчета кликов
    click_monitor = models.BooleanField(default=False, verbose_name='Мониторить клики')
    click_count = models.IntegerField('Текущее количество кликов', default=0)

    last_modified = models.DateTimeField(auto_now=True, editable=False)
    iframe = models.TextField('Код iframe', blank=True, help_text=escape(
        'Код вида: <iframe src="АДРЕС" width="200" height="300" border="0" frameborder="0" scrolling="0"></iframe>'))
    is_client_rotate = models.BooleanField(default=False, verbose_name='Ротация на клиенте')

    _files = None

    class Meta:
        verbose_name = 'размещение'
        verbose_name_plural = 'Размещение'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return 'adv:read', (self.pk,), {}

    @property
    def files(self):
        """Список файлов баннера"""

        if self._files is None:
            self._files = self.file_set.all()

        return self._files


class Limit(models.Model):
    banner = models.OneToOneField(Banner, on_delete=models.CASCADE)
    enabled = models.DateTimeField('Время включения', editable=False, null=True)
    auto_disabled = models.DateTimeField('Время автоматического выключения', editable=False, null=True)
    updated = models.DateTimeField('Время последнего обновления статистики', editable=False, null=True)
    view_limit = models.IntegerField('Огранчение просмотров', default=0)
    view_left = models.IntegerField('Просмторов осталось', default=0)
    is_active = models.BooleanField('Включен', default=False, db_index=True)

    __original_is_active = None
    __original_view_limit = None

    class Meta:
        verbose_name = 'ограничение на показы'
        verbose_name_plural = 'ограничения на показы'

    def __str__(self):
        return '{} - {}'.format(self.banner.name, self.view_limit)

    def __init__(self, *args, **kwargs):
        super(Limit, self).__init__(*args, **kwargs)
        self.__original_view_limit = self.view_limit

    def save(self, *args, **kwargs):

        self.view_left = max(self.view_left, 0)

        # Обновляем остаток если выставлен новый лимит
        if self.__original_view_limit != self.view_limit:
            self.view_left = self.view_limit

        if self.is_active and not self.__original_is_active:
            self.enabled = datetime.datetime.now()

        limit = super(Limit, self).save(*args, **kwargs)

        return limit


class Location(models.Model):
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, blank=True, null=True, verbose_name='Раздел', on_delete=models.CASCADE)
    template = models.ForeignKey(Template, blank=True, null=True, verbose_name='Страница', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'расположение'
        verbose_name_plural = 'расположение'


class Period(models.Model):
    """Период размещения баннера"""

    banner = models.ForeignKey(Banner, on_delete=models.CASCADE)
    date_from = models.DateField(db_index=True, verbose_name='Начало')
    date_to = models.DateField(db_index=True, verbose_name='Конец')

    show_time_start = models.TimeField(verbose_name='Время показа с', blank=True, null=True, editable=False)
    show_time_end = models.TimeField(verbose_name='Время показа по', blank=True, null=True, editable=False)

    class Meta:
        verbose_name = 'период размещения'
        verbose_name_plural = 'период размещения'

    def __str__(self):
        if self.date_from == self.date_to:
            return self.date_from.strftime("%d.%m.%Y")
        else:
            return u"%s-%s" % (self.date_from.strftime("%d.%m.%Y"), self.date_to.strftime("%d.%m.%Y"))


signals.post_save.connect(period_post_save, sender=Period)


def get_upload_to_path(instance, filename):
    return "%s%s" % (BANNER_ROOT, filename)


def upload_html5_file(instance, filename):
    """Возвращает путь для хранения html5 баннеров"""

    return os.path.join(BANNER_ROOT, 'html5', filename)


class File(models.Model):
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE)
    main = FileRemovableField(verbose_name='Баннер', upload_to=get_upload_to_path, blank=True, null=True,
                              validators=[validate_banner_file_extension, ])
    main_768 = FileRemovableField(verbose_name='Баннер для ширины 768', upload_to=get_upload_to_path,
                                  blank=True, null=True, validators=[validate_banner_file_extension, ])
    main_420 = FileRemovableField(verbose_name='Баннер для ширины 420', upload_to=get_upload_to_path,
                                  blank=True, null=True, validators=[validate_banner_file_extension, ])
    main_320 = FileRemovableField(verbose_name='Баннер для ширины 320', upload_to=get_upload_to_path,
                                  blank=True, null=True, validators=[validate_banner_file_extension, ])
    dummy = ImageRemovableField(verbose_name='Заглушка', upload_to=get_upload_to_path, blank=True, null=True)
    video = FileRemovableField(
        verbose_name='Видео (mp4)', upload_to=get_upload_to_path, blank=True, null=True,
        validators=[FileSizeValidator(max_size=1024 * 1024 * 16), FileExtensionValidator(allowed_extensions=['mp4'])],
        help_text='Необходим если загружен webm')
    video_ogg = FileRemovableField(
        verbose_name='Видео (ogg)', upload_to=get_upload_to_path, blank=True, null=True,
        validators=[FileSizeValidator(max_size=1024 * 1024 * 16), FileExtensionValidator(allowed_extensions=['ogg'])])
    video_webm = FileRemovableField(
        verbose_name='Видео (webm)', upload_to=get_upload_to_path, blank=True, null=True,
        validators=[FileSizeValidator(max_size=1024 * 1024 * 16), FileExtensionValidator(allowed_extensions=['webm'])],
        help_text='Необходим если загружен mp4')
    show_player = models.BooleanField(verbose_name='Отображать видео-плэйер', blank=False, default=False)
    bgimage = ImageRemovableField(verbose_name='фон (лев.)', upload_to='img/site/adv/banners/', blank=True, null=True)
    bgimage2 = ImageRemovableField(verbose_name='фон (прав.)', upload_to='img/site/adv/banners/', blank=True, null=True)
    bgcolor = ColorField('Цвет фона', blank=True, null=True)
    url = models.URLField('Ссылка', max_length=255, blank=True, null=True)
    alt = models.CharField(max_length=255, verbose_name='alt', blank=True, null=True)
    deleted = models.BooleanField('Удалить', default=False)
    text = models.CharField('Текст', max_length=300, blank=True, null=True)
    html5_url = models.URLField('Ссылка на html5 баннер', blank=True)
    html5_code = models.TextField('html5 код', blank=True)
    html5 = FileArchiveField(verbose_name='Баннер html5', upload_to=upload_html5_file, blank=True, null=True,
                             validators=[validate_html5_file, FileExtensionValidator(allowed_extensions=['zip'])])

    class Meta:
        verbose_name = 'файлы'
        verbose_name_plural = 'файлы'

    def __str__(self):
        return 'Баннер «%s»' % self.banner.name

    def get_absolute_url(self):
        if not self.link:
            return ''

        base_url = reverse('adv:banner', args=(self.banner_id, self.pk))

        return mark_safe('%s?%s' % (base_url, urllib.urlencode({
            'stat': self.pk,
            'banner': self.banner_id,
            't': int(time.time()),
        })))

    @property
    def link(self):
        if self.url:
            return self.url
        try:
            if self.banner.url:
                return self.banner.url
        except Banner.DoesNotExist:
            pass

        return ''

    @property
    def title(self):
        if self.alt:
            return self.alt
        elif self.banner.alt:
            return self.banner.alt

        return ''


signals.post_save.connect(extract_html5_banner, sender=File)


class Net(models.Model):
    """Запрещенный IP адрес для просмотра баннеров

    Используется в подсчете статистики"""

    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip


class Agent(models.Model):
    """Запрещенный User-Agent для просмотра баннеров

    Используется в подсчете статистики"""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Log(models.Model):
    """Статистика баннеров по дням"""

    ACTION_VIEW = 1
    ACTION_CLICK = 2
    ACTION_SCROLL = 3
    ACTIONS = (
        (ACTION_VIEW, 'Просмотр'),
        (ACTION_CLICK, 'Переход'),
        (ACTION_SCROLL, 'Доскролл'),
    )

    banner = models.ForeignKey(Banner, verbose_name='Баннер', on_delete=models.CASCADE)
    site = models.ForeignKey(Site, blank=True, null=True, verbose_name='Раздел', on_delete=models.CASCADE)
    action = models.PositiveSmallIntegerField(choices=ACTIONS)
    date = models.DateField(verbose_name='Дата')
    cnt = models.PositiveIntegerField()
    file = models.ForeignKey(File, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'статистика'


class CurrentLog(models.Model):
    """Статистика баннеров по 10 минут"""

    ACTION_VIEW = 1
    ACTION_CLICK = 2
    ACTION_SCROLL = 3
    ACTIONS = (
        (ACTION_VIEW, 'Просмотр'),
        (ACTION_CLICK, 'Переход'),
        (ACTION_SCROLL, 'Доскролл'),
    )

    banner = models.ForeignKey(Banner, verbose_name='Баннер', on_delete=models.CASCADE)
    action = models.PositiveSmallIntegerField(choices=ACTIONS)
    stamp = models.DateTimeField('Время')
    cnt = models.PositiveIntegerField()
    file = models.ForeignKey(File, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'статистика'


class Targetix(models.Model):
    """Код для баннеров targetix.net"""

    title = models.CharField('Название', max_length=255)
    code = models.TextField('Код')

    class Meta:
        verbose_name = 'Внешний баннер'
        verbose_name_plural = 'Внешние баннеры'

    def __str__(self):
        return self.title


class Service(models.Model):
    """Рекламные услуги"""
    name = models.CharField('Название', max_length=255)
    price = models.FloatField('Цена')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рекламная услуга'
        verbose_name_plural = 'Рекламные услуги'


class AdvOrder(BaseOrder):
    """Заказ размещения рекламы"""

    STATUS_NEW = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3
    STATUSES = (
        (STATUS_NEW, 'Новый'),
        (STATUS_APPROVED, 'Одобрен'),
        (STATUS_REJECTED, 'Отклонен'),
    )

    service = models.ForeignKey(Service, verbose_name='Рекламная услуга', related_name='order_service',
                                on_delete=models.CASCADE)
    client_name = models.CharField('Имя клиента', max_length=255, blank=True, default='')
    client_email = models.EmailField('E-mail клиента', blank=True, default='')
    client_contacts = models.CharField('Контакты клиента', max_length=1024, blank=True, default='')
    description = models.TextField('Описание')
    link = models.URLField('Ссылка', max_length=255, blank=True, null=True)
    status = models.PositiveSmallIntegerField('Статус', choices=STATUSES, default=STATUS_NEW)

    def __str__(self):
        return '{}'.format(self.client_name)

    class Meta:
        verbose_name = 'Заказ размещения рекламы'
        verbose_name_plural = 'Заказы размещения рекламы'

    def __init__(self, *args, **kwargs):
        super(AdvOrder, self).__init__(*args, **kwargs)
        self.__original_status = self.status

    def save(self, *args, **kwargs):
        from adv.order_helpers import AdvOrderHelper

        # Создать платеж если заказ одобрен
        if self.status != self.__original_status:
            order = AdvOrderHelper(self)
            if self.status == self.STATUS_APPROVED:
                invoice = order.create_invoice()
                self.invoice = invoice
                order.send_invoice()
            elif self.status == self.STATUS_REJECTED:
                order.send_rejection()

        return super(AdvOrder, self).save(*args, **kwargs)

    def get_order_helper_class(self):
        from adv.order_helpers import AdvOrderHelper
        return AdvOrderHelper
