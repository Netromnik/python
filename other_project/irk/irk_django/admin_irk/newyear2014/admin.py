# -*- coding: utf-8 -*-

from django.contrib import admin

from irk.news import admin as news_admin

from irk.newyear2014.models import Horoscope, Zodiac, Offer, Prediction, TextContest, PhotoContest, Congratulation, \
    Wallpaper, GuruAnswer, Puzzle, PhotoContestParticipant, TextContestParticipant, Photo, Article, Infographic
from irk.newyear2014.forms import CongratulationAdminForm


@admin.register(Congratulation)
class CongratulationAdmin(admin.ModelAdmin):
    """Админ поздравлений"""

    form = CongratulationAdminForm

    class Media:
        js = ('js/apps-js/admin-jq-fix.js', )


@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    """Админ гороскопов"""
    list_display = ('name', 'short_name', 'position')
    ordering = ('-position', )


@admin.register(Zodiac)
class ZodiacAdmin(admin.ModelAdmin):
    """Админ зодиаков"""
    list_display = ('name', 'horoscope', 'position')
    ordering = ('-position', )
    list_filter = ('horoscope',)


@admin.register(GuruAnswer)
class GuruAnswerAdmin(admin.ModelAdmin):
    list_display = ('content', 'gender', 'age')


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """Админ предсказаний"""


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    pass


@admin.register(TextContest)
class TextContestAdmin(admin.ModelAdmin):
    pass


@admin.register(PhotoContest)
class PhotoContestAdmin(admin.ModelAdmin):
    pass


@admin.register(PhotoContestParticipant)
class PhotoContestParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)

    class Meta:
        model = PhotoContestParticipant


@admin.register(TextContestParticipant)
class TextContestParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)

    class Meta:
        model = TextContestParticipant


@admin.register(Photo)
class NewsAdmin(news_admin.PhotoAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(news_admin.ArticleAdmin, news_admin.SectionMaterialAdmin):
    pass


@admin.register(Infographic)
class InfographicAdmin(news_admin.InfographicAdmin, news_admin.SectionMaterialAdmin):
    pass


admin.site.register(Puzzle)
admin.site.register(Wallpaper)
