# -*- coding: utf-8 -*-
import datetime

import os

from PIL import Image as PilImage, ImageDraw, ImageFont
from django.contrib import admin
from django.utils.html import linebreaks, strip_tags
from django.urls import reverse_lazy
from django.conf.urls import url
from django.http import HttpResponse
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Vacancy, Price, Page, Pricefile, Employee, Question, Faq, Condition, \
    Section, AgeGenderPercent, Interest
from .forms import QuestionAdminForm, CoordinateInlineFormset, VacancyForm, SectionAdminForm, \
    AgeGenderPercentAdminInlineFormset
from .helpers import get_price_center_coordinate, separate_thousand

from utils.helpers import inttoip
# from utils.notifications import tpl_notify
from utils.watermark import watermark


class VacancyAdmin(admin.ModelAdmin):
    form = VacancyForm
    list_display = ('name', 'start_date', 'end_date', 'update_date',)
    ordering = ('-id',)

    class Media(object):
        js = (
            'js/apps-js/admin.js',
        )


admin.site.register(Vacancy, VacancyAdmin)


class PricesInline(admin.TabularInline):
    model = Price
    extra = 1
    formset = CoordinateInlineFormset


class PageAdmin(admin.ModelAdmin):
    inlines = (PricesInline,)
    list_display = ('position', 'name', 'device', 'visible', 'price_image_link')
    list_display_links = ('name',)
    list_editable = ('position',)
    list_filter = ('device', 'visible')

    def price_image_link(self, obj):
        link = '%s?page_id=%s' % (reverse_lazy('admin:about_page_priceimagelink'), obj.pk,)
        return u'<a href="%s">скачать</a>' % link

    price_image_link.short_description = u'Цены в прайсах'
    price_image_link.allow_tags = True

    def get_urls(self):
        return [url(r'^price_image/$', self.admin_site.admin_view(self.price_image),
                    name="about_page_priceimagelink")] + super(PageAdmin, self).get_urls()

    def price_image(self, request):
        """ Генерация изображения скриншта с ценами на рекламу """

        try:
            page_id = int(request.GET.get('page_id'))
        except (TypeError, ValueError):
            raise Http404

        page = get_object_or_404(Page, pk=page_id)

        prices = Price.objects.filter(page=page)

        font_path = os.path.join(settings.BASE_PATH, "static/font/PTC55F.ttf")
        marker_img_path = os.path.join(settings.BASE_PATH, 'irk/about/static/about/img/markers')
        tmarker = PilImage.open(os.path.join(marker_img_path, 'tmarker.png'))
        bmarker = PilImage.open(os.path.join(marker_img_path, 'bmarker.png'))
        lmarker = PilImage.open(os.path.join(marker_img_path, 'lmarker.png'))
        rmarker = PilImage.open(os.path.join(marker_img_path, 'rmarker.png'))

        markers = {
            Price.TOP_POSITION: {'img': tmarker,
                                 'offset_x': -int(tmarker.size[0] / 2),
                                 'offset_y': -int(tmarker.size[1])},
            Price.BOTTOM_POSITION: {'img': bmarker,
                                    'offset_x': -int(bmarker.size[0] / 2),
                                    'offset_y': 0},
            Price.LEFT_POSITION: {'img': lmarker,
                                  'offset_x': -int(lmarker.size[0]),
                                  'offset_y': -int(lmarker.size[1] / 2)},
            Price.RIGHT_POSITION: {'img': rmarker,
                                   'offset_x': 0,
                                   'offset_y': -int(rmarker.size[1] / 2)},
        }

        img_original = PilImage.open(page.image)

        fnt_price = ImageFont.truetype(font_path, 30)
        fnt_period = ImageFont.truetype(font_path, 15)

        # Добавление фона к скриншоту
        img_bg = PilImage.new('RGBA', (img_original.size[0] + 400, img_original.size[1] + 235 + 200), '#f2dec5')
        img = watermark(img_bg, img_original, position=(200, 235))

        # Скриншот для брендирования
        # draw = ImageDraw.Draw(img)
        # draw.rectangle([40, img.size[1] - 510, img.size[0] - 40, img.size[1]], fill='#000000')
        # img = watermark(img, img_original, position=(200, img.size[1] - 500))
        # draw = ImageDraw.Draw(img)
        # draw.rectangle([200, img.size[1] - 500 + 175, img.size[0] - 201, img.size[1] - 430 + 155], fill='#ffffff')
        # draw.rectangle([200, img.size[1] - 500, img.size[0] - 200, img.size[1] - 430], fill='#000000')
        # draw.rectangle([0, img.size[1] - 100, img.size[0], img.size[1]], fill='#f2dec5')

        # Шапка
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, img.size[0], 185], fill='#ab6645')
        draw.text([200, 60], page.name, font=ImageFont.truetype(font_path, 45))

        # Блок количества просмотров
        draw.rectangle([710, 20, img.size[0] - 200, 165], fill='#844220')
        draw.text([800, 40], u'Количество просмотров', font=ImageFont.truetype(font_path, 25))
        draw.text([800, 90], separate_thousand(page.view_count_day), font=fnt_price)
        draw.text([802, 120], u'в день', font=fnt_period)
        draw.text([950, 90], separate_thousand(page.view_count_week), font=fnt_price)
        draw.text([952, 120], u'в неделю', font=fnt_period)

        for price in prices:

            offset_x = 200
            offset_y = 235
            text_offset_x = 15
            text_offset_y = 0

            if price.format != u'Брендирование':

                high, width = price.height_width.split(',')

                if int(high) or int(width):

                    if price.marker_position == Price.TOP_POSITION:
                        offset_y -= int(int(price.height_width.split(',')[0]) / 2)
                    if price.marker_position == Price.BOTTOM_POSITION:
                        offset_y += int(int(price.height_width.split(',')[0]) / 2)
                        text_offset_y += 15
                    if price.marker_position == Price.LEFT_POSITION:
                        offset_x -= int(int(price.height_width.split(',')[1]) / 2)
                    if price.marker_position == Price.RIGHT_POSITION:
                        offset_x += int(int(price.height_width.split(',')[1]) / 2)
                        text_offset_x += 30

                    # Рисование маркера
                    marker = markers[price.marker_position]
                    position = get_price_center_coordinate(price)
                    position = (position[0] + marker['offset_x'] + offset_x,
                                position[1] + marker['offset_y'] + offset_y)
                    img = watermark(img, marker['img'], position=position)

                    # Рисование текста
                    draw = ImageDraw.Draw(img)
                    text_position = (position[0] + text_offset_x, position[1] + text_offset_y)
                    draw.text(text_position, separate_thousand(price.value), font=fnt_price)
                    draw.text((text_position[0] + 2, text_position[1] + 30), price.get_period_display(),
                              font=fnt_period)
            else:
                pass
                # Маркер брендирования рисуется отдельно по фиксированой координате
                # text_offset_x += 30
                # draw = ImageDraw.Draw(img)
                # draw.text([550, img.size[1] - 490], u'Брендирование', font=fnt_price)
                # img = watermark(img, rmarker, position=(800, img.size[1] - 495))
                # draw = ImageDraw.Draw(img)
                # text_position = (800 + text_offset_x, img.size[1] - 495 + text_offset_y)
                # draw.text(text_position, separate_thousand(price.value), font=fnt_price)
                # draw.text((text_position[0] + 2, text_position[1] + 30), price.get_period_display(), font=fnt_period)

        response = HttpResponse(content_type="image/jpeg")
        img.save(response, "JPEG", quality=100)
        return response


admin.site.register(Page, PageAdmin)


class PricefileAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Pricefile, PricefileAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display_links = ('title',)
    list_display = ('position', 'title', 'job', 'is_op', 'is_head_op')
    list_editable = ('position', )


admin.site.register(Employee, EmployeeAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'is_replied', 'created')
    list_filter = ('is_replied',)
    list_select_related = True
    readonly_fields = ('user_content', 'user_name', 'user_email', 'user_ip', 'respondent', 'replied')
    form = QuestionAdminForm
    ordering = ('-id',)

    def user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() if len(obj.user.get_full_name()) else obj.user.username
        return obj.name

    user_name.short_description = u'Имя пользователя'

    def user_email(self, obj):
        if obj.user:
            return obj.user.email
        return obj.email

    user_email.short_description = u'E-mail'

    def user_ip(self, obj):
        return inttoip(obj.ip)

    user_ip.short_description = u'IP'

    def user_content(self, obj):
        return linebreaks(strip_tags(obj.content))

    user_content.short_description = u'Вопрос'
    user_content.allow_tags = True

    def save_model(self, request, obj, form, change):
        """
                        !TODO: CELERY
        """
        if not obj.is_replied and len(obj.content) > 0:
            # Отправляем письмо
            obj.is_replied = True
            obj.respondent = request.user
            obj.replied = datetime.datetime.now()
            # sender = u'%s <%s>' % (
            #     request.user.get_full_name() if len(request.user.get_full_name()) > 0 else request.user.username,
            #     request.user.email)
            # tpl_notify(u'Ответ на ваш вопрос на сайте IRK.ru', 'about/notif/question_reply.html',
            #            {'object': obj}, request, emails=[obj.email if obj.email else obj.user.email, ], sender=sender)
        obj.save()


admin.site.register(Question, QuestionAdmin)


class ConditionAdmin(admin.ModelAdmin):
    list_display = ('position', 'name',)
    list_display_links = ('name',)
    list_editable = ('position', )


admin.site.register(Condition, ConditionAdmin)


class FaqAdmin(admin.ModelAdmin):
    list_display = ('position', 'name',)
    list_display_links = ('name',)
    list_editable = ('position', )


admin.site.register(Faq, FaqAdmin)


class InterestsInline(admin.TabularInline):
    model = Interest
    extra = 1


class AgeGenderPercentInline(admin.TabularInline):
    model = AgeGenderPercent
    formset = AgeGenderPercentAdminInlineFormset
    extra = 1


class SectionAdmin(admin.ModelAdmin):
    inlines = (InterestsInline, AgeGenderPercentInline)
    list_display = ('position', 'name', 'statistic_date')
    list_display_links = ('name',)
    list_editable = ('position', )
    list_filter = ('in_audience', 'in_mediakit')
    form = SectionAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'position', 'statistic_date', 'in_audience', 'in_mediakit', 'pages',
                       'is_general', 'device_pc_percent', 'device_mobile_percent'),
        }),
        (u'Аудитория', {
            'fields': ('audience_text', )
        }),
        (u'Медиакит', {
            'fields': ('mediakit_color', 'mediakit_title', 'mediakit_main_screenshot',
                       'mediakit_attraction_title', 'mediakit_attraction_text', 'mediakit_attraction_screenshot',
                       'mediakit_statistic_title', 'mediakit_audience_title',
                       'mediakit_benefit_title', 'mediakit_benefit_text')
        }),
    )


admin.site.register(Section, SectionAdmin)
