# -*- coding: utf-8 -*-

from rest_framework import serializers

from irk.news.models import News, Flash
from irk.api.fields import TypographField, GalleryRelatedField


class NewsListSerializer(serializers.ModelSerializer):
    title = TypographField(source='title')
    caption = TypographField(source='caption')
    date = serializers.Field(source='stamp')

    images = GalleryRelatedField(source='gallery', read_only=True)

    class Meta:
        model = News
        fields = ('id', 'date', 'slug', 'title', 'caption', 'images', 'category')


class NewsReadSerializer(NewsListSerializer):
    content = TypographField(source='content')

    class Meta(NewsListSerializer.Meta):
        fields = NewsListSerializer.Meta.fields + ('content', 'author', )


class FlashCreateSerializer(serializers.ModelSerializer):
    """ Создание народных новостей мз смс"""

    class Meta:
        model = Flash
        fields = ('username', 'content', 'type')
