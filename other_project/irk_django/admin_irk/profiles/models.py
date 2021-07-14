# -*- coding: utf-8 -*-

import datetime
import os
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.db.models.signals import post_save
from pytils.translit import slugify

from irk.authentication.settings import USERNAME_REGEXP
from irk.comments.models import CommentGenericForeignKey
from irk.profiles.signals import create_blank_avatar, set_subscriber
from irk.utils.fields.file import ImageRemovableField
from irk.utils.files import generate_file_name

try:
    from django.contrib.auth.models import get_hexdigest
except ImportError:
    from irk.authentication.helpers import get_hexdigest


# Удаляем валидатор, проверяющий значение поля `User.username` регулярным выражением. зашитым в django
# и добавляем свой валидатор с регуляркой
for field in User._meta.concrete_fields:
    if field.name != 'username':
        continue

    for idx, validator in enumerate(field.validators):
        if isinstance(validator, RegexValidator):
            field.validators.pop(idx)
            field.validators.append(RegexValidator(USERNAME_REGEXP))
            break


def get_user_image_path(instance, filename):
    """ Функция возвращает путь для upload`а картинки с разбивкой на группы по 500 файлов. """
    folder = Profile.objects.count() / 500 + 1

    return 'img/site/profiles/%d/%s' % (folder, generate_file_name(None, filename))


class Profile(models.Model):
    """Модель профиля пользователя"""

    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'
    GENDER_CHOICES = (
        (GENDER_MALE, u'мужской'),
        (GENDER_FEMALE, u'женский')
    )

    TYPE_PERSONAL = 0
    TYPE_CORPORATIVE = 1
    TYPE_CHOICES = (
        (TYPE_PERSONAL, u'личный'),
        (TYPE_CORPORATIVE, u'корпоративный'),
    )

    full_name = models.CharField(u'Видимое имя', max_length=100)
    user = models.OneToOneField(User)
    is_banned = models.BooleanField(u'Заблокирован', default=False, blank=True)
    is_closed = models.BooleanField(u'Закрыт', default=False, blank=True)
    bann_end = models.DateTimeField(u'Дата, до которой заблокирован', null=True, blank=True)
    hash = models.CharField(max_length=40, editable=False)
    hash_stamp = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now, editable=False)
    is_moderator = models.BooleanField(default=False)
    mname = models.CharField(u'Отчество', max_length=100, blank=True)
    gender = models.CharField(u'Пол', max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.CharField(u'Адрес', max_length=255, blank=True)
    phone = models.CharField(u'Телефон', max_length=20, blank=True)
    birthday = models.DateField(u'Дата рождения', null=True, blank=True)
    subscribe = models.BooleanField(u'Подписка на рассылку новостей', default=False)
    comments_notify = models.BooleanField(u'Уведомлять об ответах на мои отзывы', default=True)
    session_id = models.CharField(max_length=32, editable=False)
    description = models.TextField(u'Описание', blank=True)
    image = ImageRemovableField(verbose_name=u'фотография', upload_to=get_user_image_path, blank=True)
    rating_votes_cnt = models.IntegerField(verbose_name=u'Количество голосов', help_text=u'Для рейтингов задач',
                                           editable=False, default=10)
    signature = models.CharField(u'Подпись', max_length=255, blank=True)
    is_verified = models.BooleanField(u'Подтвержденный пользователь', default=False, editable=False)
    type = models.PositiveSmallIntegerField(u'Тип', default=TYPE_PERSONAL, choices=TYPE_CHOICES)
    company_name = models.CharField(u'Название компании', max_length=255, blank=True)
    business_account = models.ForeignKey('adv_cabinet.BusinessAccount', null=True, blank=True,
                                         verbose_name=u'Бизнес аккаунт')

    class Meta:
        verbose_name = u'профиль'
        verbose_name_plural = u'профиль'
        permissions = (("can_ban_profile", u"Can ban profile"),)

    def __unicode__(self):
        if self.type == self.TYPE_CORPORATIVE:
            return self.company_name or self.full_name

        return self.full_name

    def is_business_account(self):
        return bool(self.business_account)

    def is_personal(self):
        return self.type == self.TYPE_PERSONAL

    def is_corporative(self):
        return self.type == self.TYPE_CORPORATIVE

    def create_hash(self):
        """Создает временный хеш для подтверждения регистрации, либо для восстановления пароля."""

        algo = 'sha1'
        if not self.hash or self.user.is_active:
            self.hash = get_hexdigest(algo, str(random.random()), str(random.random()))
        self.hash_stamp = datetime.datetime.now()

    @property
    def avatar(self):
        """Аватарка пользователя

        Если не заполнена, возвращается изображение по умолчанию"""

        if self.image and os.path.exists(os.path.join(settings.MEDIA_ROOT, self.image.name)):
            return self.image

        name = 'img/new_makeup/blank_avatar_woman.jpg' if self.gender == 'f' else 'img/new_makeup/blank_avatar_man.jpg'

        return ImageFieldFile(instance=None, field=models.ImageField(), name=name)

    def get_absolute_url(self):
        return reverse('profiles:read', args=(self.user_id, slugify(self.full_name or self.user.username)))

    # TODO: Refactor: rename to is_banned
    def is_ban(self):
        if not self.is_banned:
            return False

        if not self.bann_end:
            return True

        if self.bann_end < datetime.datetime.now():
            return False

        return True


post_save.connect(set_subscriber, sender=Profile)
post_save.connect(create_blank_avatar, sender=Profile)


# TODO: перенести в приложение `options`
def _user_unicode(self):
    try:
        return self.profile.full_name or self.username
    except Profile.DoesNotExist:
        return self.username


User.__unicode__ = _user_unicode


def _user_get_full_name(self):
    try:
        return self.profile.full_name or self.username
    except Profile.DoesNotExist:
        return self.username


User.get_full_name = _user_get_full_name


def _user_get_absolute_url(self):
    return self.profile.get_absolute_url()


User.get_absolute_url = _user_get_absolute_url


class Counter(models.Model):
    """Счетчики сообщений в форуме, объявлений"""

    user = models.ForeignKey(User)
    model = models.ForeignKey(ContentType)
    value = models.PositiveIntegerField()
    state = models.PositiveIntegerField(null=True, blank=True)


# TODO: перенести в приложение `options`
class Options(models.Model):
    user = models.ForeignKey(User)
    param = models.CharField(max_length=100)
    value = models.TextField()


class UserBanHistory(models.Model):
    moderator = models.ForeignKey(User, related_name='banned', null=True)
    user = models.ForeignKey(User, related_name='bans')
    reason = models.TextField(blank=True)
    created = models.DateTimeField()
    ended = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = u'история банов пользователей'
        verbose_name_plural = u'история банов пользователей'


class ProfileBannedUser(Profile):
    """Прокси-модель для списка забаненных пользователей"""

    class Meta:
        proxy = True
        verbose_name = u'пользователь (бан)'
        verbose_name_plural = u'бан лист логинов'


class ProfileSocial(models.Model):
    TYPE_VK = 0
    TYPE_OK = 1
    TYPE_TWITTER = 2
    TYPE_FACEBOOK = 3
    TYPE_INSTAGRAM = 4

    TYPE_CHOICES = (
        (TYPE_VK, u'Вконтакте'),
        (TYPE_OK, u'Одноклассники'),
        (TYPE_TWITTER, u'Твиттер'),
        (TYPE_FACEBOOK, u'Фейсбук'),
        (TYPE_INSTAGRAM, u'Instagram'),
    )

    TYPE_SLUGS = {
        TYPE_VK: 'vk',
        TYPE_OK: 'ok',
        TYPE_TWITTER: 'tw',
        TYPE_FACEBOOK: 'fb',
        TYPE_INSTAGRAM: 'ig',
    }

    profile = models.ForeignKey(Profile, related_name='social')
    type = models.PositiveSmallIntegerField(u'Тип', choices=TYPE_CHOICES)
    url = models.URLField(u'Ссылка')

    class Meta:
        db_table = 'profiles_social'
        verbose_name = u'социальная сеть'
        verbose_name_plural = u'социальные сети'

    def __unicode__(self):
        return u'{}: {}'.format(self.get_type_display(), self.url)

    def get_type_slug(self):
        return self.TYPE_SLUGS.get(self.type)


class Bookmark(models.Model):
    user = models.ForeignKey(User)
    created = models.DateTimeField(u'Дата добавления', auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(db_index=True)
    target = CommentGenericForeignKey('content_type', 'target_id')

    class Meta:
        verbose_name = u'закладка'
        verbose_name_plural = u'закладки'


class BounceEvent(models.Model):
    """
    Событие, описывающее недоставленное пользователю письмо
    см. irk.utils.bounce
    """

    # type = models.CharField('Тип сообщения', null=False, blank=True, default='', max_length=30)
    email = models.CharField('Электронная почта', null=False, blank=True, max_length=190, default='')
    message_date = models.DateTimeField('Дата и время письма', null=True)
    date = models.DateField('Дата письма', null=True)
    message_id = models.CharField(null=False, blank=True, default='', max_length=150)
    hash = models.CharField('Хеш письма', max_length=50, null=False, blank=True, default='')
    details = models.TextField(null=False, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    user = models.ForeignKey(User, blank=True, null=True, related_name='bounces')

    class Meta:
        verbose_name = 'Баунс-письмо'
        verbose_name_plural = 'Баунс-письма'

    def __unicode__(self):
        return '<Bounce object {}>'.format(self.id)
