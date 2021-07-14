# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from rest_framework import serializers


class LogListSerializer(serializers.Serializer):
    date = serializers.DateField()
    views = serializers.IntegerField()
    scrolls = serializers.IntegerField()
    clicks = serializers.IntegerField()
    ctr = serializers.FloatField()


class PeriodListSerializer(serializers.Serializer):
    site = serializers.CharField()
    place = serializers.CharField()


class BannerListSerializer(serializers.Serializer):
    period = serializers.CharField()
    places = PeriodListSerializer(many=True)
    link = serializers.URLField()
