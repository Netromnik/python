# -*- coding: utf-8 -*-

import datetime
import re
import zipfile

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.utils import ValidationError
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from irk.gallery.models import Gallery
from irk.map.models import Cities
from irk.news.forms.fields import SubjectAutocompleteField, NewsAutocompleteField, \
    MaterialAutocompleteField, TagsAutocompleteField, LongreadAutocompleteField
from irk.news.models import News, Category, Flash, UrgentNews, Live, LiveEntry, Article, Video, \
    Photo, Infographic, Mailer, Subscriber, ArticleType, Quote, Position, Metamaterial, \
    SocialPultUpload, TildaArticle
from irk.options.models import Site
from irk.phones.models import Firms
from irk.utils.decorators import strip_fields
from irk.utils.fields.file import AdminImagePreviewWidget, AdminImageReadonlyWidget
from irk.utils.helpers import get_object_or_none
from irk.utils.templatetags.str_utils import do_typograph
from irk.utils.fields.geo import PointCharField


NEWS_SLUG_RE = NEWS_ALIAS_RE = re.compile(r'^[a-z]+$')


class BaseMaterialAdminForm(forms.ModelForm):
    """Базовая форма для материалов в админке"""

    subject = SubjectAutocompleteField(label=u'Сюжет', required=False)
    tags = TagsAutocompleteField(label=u'Теги', required=False)
    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.filter(Q(is_hidden=False) | Q(slugs='magazine')), label=u'Разделы',
        widget=forms.SelectMultiple(attrs={'size': '10'})
    )

    # Поля для вставки bb-кода [material id]
    # TODO: удалить после создания крутого редактора статей
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    related_material = LongreadAutocompleteField(label=u'Материал', required=False)

    social_card = forms.ImageField(widget=AdminImageReadonlyWidget(), required=False, label=u'Результат')
    magazine_image = forms.ImageField(widget=AdminImagePreviewWidget(), required=False, label=u'Фото для журнала')

    class Meta:
        widgets = {
            'social_text': forms.Textarea(attrs={'maxlength': 100}),
        }

    def __init__(self, *args, **kwargs):
        super(BaseMaterialAdminForm, self).__init__(*args, **kwargs)

        if not self.instance.pk:
            self.initial['stamp'] = datetime.date.today()

        self._home_site = Site.objects.get(slugs='home')

    def save(self, *args, **kwargs):
        if not self.instance.created:
            self.instance.created = datetime.datetime.now()
        self.instance.updated = datetime.datetime.now()

        # Автозаполнение текста карточки для социальных сетей
        if not self.instance.social_text:
            self.instance.social_text = self.instance.title[:100]
            self.changed_data.append('social_text')

        return super(BaseMaterialAdminForm, self).save(*args, **kwargs)

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug and not NEWS_SLUG_RE.match(slug):
            raise forms.ValidationError(u'Алиас новости должен состоять из строчных букв английского алфавита')

        stamp = self.cleaned_data.get('stamp')
        model = self._meta.model
        if stamp:
            if self.instance:
                is_exists = model.objects.filter(stamp=stamp, slug=slug).exclude(pk=self.instance.pk).exists()
            else:
                is_exists = model.objects.filter(stamp=stamp, slug=slug).exists()
            if is_exists:
                raise forms.ValidationError(u'Сегодня уже есть новость с таким алиасом')

        return slug

    def clean_caption(self):
        return self.cleaned_data.get('caption', '').strip()

    def clean_content(self):
        """Проверка, что в bb-кодах используются картинки относящиеся к материалу"""

        content = self.cleaned_data.get('content')

        content_images = self._get_images_from(content)
        gallery_images = self._get_gallery_images()

        wrong_images = content_images - gallery_images
        if wrong_images:
            raise forms.ValidationError(
                u'Использованы изображения не относящиеся к материалу. Номера: %(ids)s',
                code='invalid',
                params={'ids': u' ,'.join(map(str, wrong_images))}
            )

        return content

    def _get_images_from(self, content):
        """
        Получить идентификаторы изображений из контента.

        Проверяются bb-коды: image, images, diff, vladiff

        :param str content: текст в котором ищем изображения
        :return set: список идентификаторов
        """

        # Считаем, что идентификатор не может быть меньше 6 цифр
        image_id_pattern = re.compile(r'\d{6,}')
        # Регулярки для обработки bb-кодов
        patterns = [
            re.compile(r'\[\s*image (\d+)\]'),              # [image]
            re.compile(r'\[\s*images (.+)\s*\]'),          # [images]
            re.compile(r'\[\s*(?:vla)?diff (.+)\s*\]'),     # [diff] and [vladiff]
        ]

        images_ids = set()
        for pattern in patterns:
            for result in pattern.findall(content):
                for item in image_id_pattern.findall(result):
                    images_ids.add(int(item))

        return images_ids

    def _get_gallery_images(self):
        """
        Получить изображения галереи, относящейся к материалу.

        :return set: список идентификаторов изображений из галереи материала
        """

        gallery_id = self.data.get('gallerypicture_set-0-gallery')
        gallery = get_object_or_none(Gallery, pk=gallery_id)
        if not gallery:
            return set()

        return set(gallery.gallerypicture_set.values_list('id', flat=True))


@strip_fields
class NewsAdminForm(BaseMaterialAdminForm):
    """Форма для новостей в админке"""

    city = forms.ModelChoiceField(label=u'Город',
        queryset=Cities.objects.filter(Q(cites__slugs='news') | Q(alias='irkutsk')).distinct())
    bunch = NewsAutocompleteField(label=u'Предыдущая связанная новость', required=False)
    official_comment_text = forms.CharField(label=u'Текст', required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': '250'}),
        help_text=u'Максимум 300 символов. Любые теги запрещены')

    class Meta(BaseMaterialAdminForm.Meta):
        help_texts = {
            'caption': u'190 знаков',
        }
        widgets = {
            'caption': forms.Textarea(attrs={'maxlength': 190})
        }

    def __init__(self, *args, **kwargs):
        super(NewsAdminForm, self).__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields['city'].initial = Cities.objects.get(alias='irkutsk')

    def clean_bunch(self):
        bunch = self.cleaned_data.get('bunch')
        if self.instance and self.instance == bunch:
            raise forms.ValidationError(u"Нельзя связывать с текущей новостью")
        return bunch


class ArticleAdminForm(BaseMaterialAdminForm):
    """Форма для статей в админке"""

    image = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Широкоформатная фотография',
        help_text=u'Размер: 1180х560 пикселей'
    )
    header_image = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Фоновая фотография шапки',
        help_text=u'Размер: 1920х600 пикселей'
    )

    class Meta(BaseMaterialAdminForm.Meta):
        help_texts = {
            'caption': u'70 знаков',
            'magazine_position': u'4 позиция только для теста\n5 позиция только для фоторепортажа'
        }
        widgets = {
            'caption': forms.Textarea(attrs={'maxlength': 70})
        }

    def __init__(self, *args, **kwargs):
        super(ArticleAdminForm, self).__init__(*args, **kwargs)

        if not self.initial.get('type'):
            self.initial['type'] = ArticleType.objects.order_by('id')[0]

    def clean(self):
        data = super(ArticleAdminForm, self).clean()

        self._validate_image(data)
        self._validate_header_image(data)

        return data

    def _validate_image(self, data):
        is_hidden = data.get('is_hidden')
        image = data.get('image')

        if not is_hidden and not image:
            err = forms.ValidationError(u'Для открытия статьи загрузите фотографию')
            self.add_error('image', err)

    def _validate_header_image(self, data):
        """Для шаблона Фото в шапке обязательно нужно фото"""
        is_hidden = data.get('is_hidden')
        header_image = data.get('header_image')
        template = data.get('template')

        if (template == Article.TEMPLATE_IMAGE_HEADER
                and not is_hidden
                and not header_image
           ):
            err = forms.ValidationError(u'Для открытия статьи загрузите фото для шапки')
            self.add_error('header_image', err)
            self.add_error('', err)


class TildaArticleAdminForm(BaseMaterialAdminForm):
    """Форма редактирования TildaArticle"""

    class Meta(BaseMaterialAdminForm.Meta):
        model = TildaArticle
        fields = '__all__'  # не очень

        help_texts = {
            'caption': u'70 знаков',
        }
        widgets = {
            'caption': forms.TextInput(attrs={'maxlength': 70, 'size': 80})
        }

    def clean_archive(self):
        """Валидация архива при загрузке в админке"""
        archive = self.cleaned_data.get('archive')
        if hasattr(archive, 'seek'):
            if not zipfile.is_zipfile(archive):
                raise forms.ValidationError(u'Файл не является зип-архивом', code='invalid')

        return archive

    def clean(self):
        data = super(TildaArticleAdminForm, self).clean()

        is_hidden = data.get('is_hidden')
        image = data.get('image')

        if not is_hidden and not image:
            raise forms.ValidationError(u'Для открытия статьи необходимо заполнить поле "Широкоформатная фотография"')
        return data


class PhotoAdminForm(BaseMaterialAdminForm):
    """Форма для фоторепортажей в админке"""

    image = forms.ImageField(widget=AdminImagePreviewWidget(), required=False, label=u'Широкоформатная фотография',
                             help_text=u'Размер: 1180х560 пикселей')

    class Meta(BaseMaterialAdminForm.Meta):
        help_texts = {
            'magazine_position': u'Фотореп можно ставить только на 5 позицию'
        }

    def clean(self):
        data = super(PhotoAdminForm, self).clean()

        is_hidden = data.get('is_hidden')
        image = data.get('image')

        if not is_hidden and not image:
            raise forms.ValidationError(u'Для открытия фоторепортажа необходимо заполнить поле '
                                        u'"Широкоформатная фотография"')
        return data


class VideoAdminForm(BaseMaterialAdminForm):
    """Форма для видео в админке"""


class InfographicAdminForm(BaseMaterialAdminForm):
    """Форма для инфографики в админке"""


class PodcastAdminForm(BaseMaterialAdminForm):
    """Форма для инфографики в админке"""


class CategoryAdminForm(forms.ModelForm):
    """Форма редактирования категорий новостей для админки"""

    class Meta:
        model = Category
        fields = ('is_custom', 'title', 'slug', 'image')


class FlashForm(forms.ModelForm):
    title = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': u'Текст новости (не короче 10 и не длиннее 255 символов)'}))

    class Meta:
        model = Flash
        fields = ('title', 'content')

    def clean_title(self):
        title = self.cleaned_data.get('title', '')

        cleaned_title = do_typograph(re.sub(r'\s+', '', title), 'user,false')
        if len(cleaned_title) < 10:
            raise forms.ValidationError(u'Длина сообщения должна быть больше десяти символов')

        return title


class UrgentNewsAdminForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, label=u'Текст')

    class Meta:
        model = UrgentNews
        fields = ('text', 'is_visible')


def validate_subscription_email(email):

    subscriber_count = Subscriber.objects.filter(email=email).count()

    if subscriber_count:
        raise ValidationError(u'%s уже подписан на рассылку' % email)


class SubscriptionForm(forms.Form):
    """Форма Подписки на новости для пользователей"""

    email = forms.EmailField(label=u'Email', validators=[validate_subscription_email])


class SubscriptionAnonymousForm(SubscriptionForm):
    """Форма Подписки на новости для анонимов"""

    captcha = ReCaptchaField(label=u'Контрольные цифры:', widget=ReCaptchaWidget())


class LiveAdminForm(forms.ModelForm):
    news = forms.ModelChoiceField(queryset=News.objects.all(), label=u'Новость')

    def __init__(self, *args, **kwargs):
        super(LiveAdminForm, self).__init__(*args, **kwargs)

        choices = [('', '----------'),]
        for entry in News.objects.filter(is_hidden=False).order_by('-stamp', '-pk')[:30]:
            choices.append((entry.pk, unicode(entry)))
        self.fields['news'].choices = choices

    def clean(self):
        news = self.cleaned_data.get('news')

        queryset = Live.objects.filter(news=news)
        if self.instance:
            queryset = queryset.exclude(news_id=self.instance.news_id)
        if queryset.count() > 0:
            raise forms.ValidationError(u'К этой новости уже привязана live трансляция')

        return self.cleaned_data


class LiveEntryForm(forms.ModelForm):
    created = forms.TimeField(label=u'Время', required=False)

    def clean(self):
        data = self.cleaned_data
        text = data.get('text')
        image = data.get('image')
        if not text and not image:
            raise forms.ValidationError(u'Поле текст или картинка должны быть заполнены обязательно')

        return data

    class Meta:
        model = LiveEntry
        fields = ('text', 'is_important', 'created', 'image', 'date')


class MailerAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MailerAdminForm, self).__init__(*args, **kwargs)
        # Берем список адресов из последней оправленной рассылки
        if not 'mails' in self.initial or not self.initial['mails']:
            try:
                mailer = Mailer.objects.all().order_by('-stamp')[0]
                self.initial['mails'] = mailer.mails
            except (IndexError, AttributeError):
                pass

    class Meta:
        model = Mailer
        fields = ('mails', 'title', 'text', 'file',)


class QuoteAdminForm(forms.ModelForm):
    """Форма цитат в админе"""

    def __init__(self, *args, **kwargs):
        super(QuoteAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.object:
            self.fields['object_content_type'].initial = self.instance.object.title

    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    content_type = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    object_content_type = MaterialAutocompleteField(label=u'Материал', required=True)

    class Meta:
        model = Quote
        fields = ('title', 'text', 'is_hidden', 'object_content_type', 'object_id', 'content_type')

    def clean_content_type(self):
        content_type = self.cleaned_data.get('content_type')
        content_type = ContentType.objects.get(pk=content_type)
        return content_type


class PositionAdminForm(forms.ModelForm):
    """Форма позиций в админе"""

    def __init__(self, *args, **kwargs):
        super(PositionAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.material:
            self.fields['object_content_type'].initial = self.instance.material.title_with_type()

    object_content_type = MaterialAutocompleteField(label=u'Материал', required=True)
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    content_type = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Position
        fields = ('number', 'object_content_type', 'object_id', 'content_type')

    def clean_content_type(self):
        content_type_id = self.cleaned_data.get('content_type')
        if content_type_id:
            return ContentType.objects.get(pk=content_type_id)


class MetamaterialAdminForm(BaseMaterialAdminForm):
    """Форма для фоторепортажей в админке"""

    image = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Широкоформатная фотография',
        help_text=u'Размер: 1180х560 пикселей'
    )
    image_3x2 = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Стандартная фотография',
        help_text=u'Размер: 705х470. Пропорция 3:2. Используется когда метаматериал является спецпроектом.'
    )

    class Meta(BaseMaterialAdminForm.Meta):
        model = Metamaterial
        fields = '__all__'

        help_texts = {
            'is_special': u'также потребуется загрузить Стандартную фотографию',
            'show_on_home': u'прежде необходимо отметить галочку Спецпроект',
        }

    def clean(self):
        cleaned_data = super(MetamaterialAdminForm, self).clean()

        is_hidden = cleaned_data.get('is_hidden')
        image = cleaned_data.get('image')

        if not is_hidden and not image:
            raise forms.ValidationError(u'Для открытия метаматериала необходимо заполнить поле '
                                        u'"Широкоформатная фотография"')

        is_special = cleaned_data.get('is_special')
        show_on_home = cleaned_data.get('show_on_home')
        image_3x2 = cleaned_data.get('image_3x2')

        if show_on_home and not is_special:
            raise forms.ValidationError(u'Отображать на главной в блоке Спецпроектов можно только метаматериалы '
                                        u'отмеченные галочкой "Спецпроект"')

        if is_special and not image_3x2:
            raise forms.ValidationError(u'Для метаматериала спецпроекта необходимо заполнить поле '
                                        u'"Стандартная фотография"')
        return cleaned_data


class SubjectAdminForm(forms.ModelForm):

    social_card = forms.ImageField(widget=AdminImageReadonlyWidget(), required=False, label=u'Результат')

    class Meta:
        widgets = {
            'social_text': forms.Textarea(attrs={'maxlength': 100}),
        }

    def save(self, *args, **kwargs):
        # Автозаполнение текста карточки для социальных сетей
        if not self.instance.social_text:
            self.instance.social_text = self.instance.title[:100]
            self.changed_data.append('social_text')

        return super(SubjectAdminForm, self).save(*args, **kwargs)


class SocialPultUploadForm(forms.ModelForm):
    """Форма загрузки изображения в редактор соцсетей"""

    class Meta:
        model = SocialPultUpload
        fields = ['image']
