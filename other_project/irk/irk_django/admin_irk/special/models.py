# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save, post_delete

from irk.options.models import Site
from irk.utils.db.models.fields import ColorField
from irk.utils.fields.file import FileRemovableField, ImageRemovableField
from irk.adv.models import Place

from irk.special.cache import invalidate


class Project(models.Model):
    """Специальный проект"""

    slug = models.SlugField(u'Алиас', unique=True)
    title = models.CharField(u'Название', max_length=255)
    description = models.TextField(u'Описание')
    color = ColorField(u'Цвет')
    site = models.ForeignKey(Site, related_name='project', verbose_name=u'Раздел')
    branding = ImageRemovableField(
        verbose_name=u'Брендирование', upload_to='img/site/special/branding',
        help_text=u'Размеры изображения: 1920×600 пикселей') # min_size=(1920, 600), max_size=(1920, 600)
    html_head = models.TextField(u'HTML под шапкой', blank=True)
    image = models.ImageField(
        verbose_name=u'Широкоформатная фотография', upload_to='img/site/special/project',
        help_text=u'Размер: 940х445 пикселей', blank=True
    )
    show_on_home = models.BooleanField(u'Показывать в блоке Спецпроектов на главной', default=False, db_index=True)
    icon = FileRemovableField(verbose_name=u'иконка в формате SVG', upload_to='img/site/news/subject/icon',
                              blank=True, null=True, help_text=u'Размер изображения: 31x31',
                              validators=[FileExtensionValidator(allowed_extensions=['svg'])])

    branding_top = models.ForeignKey(Place, verbose_name=u'Позиция брендирования вверху страницы', null=True,
                                     related_name='project_branding_top', blank=True)
    branding_bottom = models.ForeignKey(Place, verbose_name=u'Позиция брендирования внизу страницы', null=True,
                                        related_name='project_branding_bottom', blank=True)
    banner_right = models.ForeignKey(Place, verbose_name=u'Позиция баннера в правой колонке статей', null=True,
                                     related_name='project_banner_right', blank=True)

    class Meta:
        verbose_name = u'Спецпроект'
        verbose_name_plural = u'Спецпроекты'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.slug == 'columnist':
            return reverse('obed:index') + '?tab=critic#article-list'

        return reverse('special:index', kwargs={'slug': self.slug})

    @property
    def wide_image(self):
        """Широкоформатное изображение"""

        return self.image


class Sponsor(models.Model):
    """Спонсоры спецпроектов"""

    project = models.ForeignKey(Project, verbose_name=u'Спецпроект')
    name = models.CharField(u'Название', max_length=255)
    link = models.URLField(u'Ссылка', blank=True)
    image = models.ImageField(
        verbose_name=u'Логотип', upload_to='img/site/special/project/sponsor/',
    )

    class Meta:
        verbose_name = u'Спонсор'
        verbose_name_plural = u'Спонсоры'

    def __unicode__(self):
        return self.name


class ProjectMixin(models.Model):
    """Примесь для моделей доступных в спецпроектах"""

    project = models.ForeignKey(Project, null=True, blank=True, verbose_name=u'Спецпроект',
                                related_name='project_%(class)s', default=None)

    class Meta:
        abstract = True


post_save.connect(invalidate, sender=Project)
post_delete.connect(invalidate, sender=Project)
