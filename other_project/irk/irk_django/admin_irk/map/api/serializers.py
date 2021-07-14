# -*- coding: utf-8 -*-

from rest_framework import serializers, fields

from irk.map.models import Cities as City


class CitySerializer(serializers.ModelSerializer):
    name_genitive = fields.Field(source='genitive_name')
    name_prepositional = fields.Field(source='predl_name')
    name_dative = fields.Field(source='datif_name')
    slug = fields.Field(source='alias')

    class Meta:
        model = City
        fields = ('id', 'name', 'name_genitive', 'name_prepositional', 'name_dative', 'slug', 'center')
