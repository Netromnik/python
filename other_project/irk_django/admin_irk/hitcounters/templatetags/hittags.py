# -*- coding: utf-8 -*-

import logging

import redis
from django import template

from irk.hitcounters.settings import REDIS_DB
from irk.hitcounters.helpers import get_hitcounter_info


register = template.Library()


class HitCounterNode(template.Node):

    def __init__(self, obj, as_var=None):
        self.object = template.Variable(obj)
        self.as_var = as_var

    def render(self, context):
        value = ''
        obj = self.object.resolve(context)
        info = get_hitcounter_info(obj)
        if info:
            value = getattr(obj, info['db_field'], 0)
            red_conn = redis.StrictRedis(
                host=REDIS_DB['HOST'], db=REDIS_DB['DB'])
            obj_key = "object_%s_%s" % (info['obj_type'], obj.pk)
            try:
                value += int(red_conn.get(obj_key)) or 0
            except (TypeError, ValueError):
                pass

        if self.as_var:
            context[self.as_var] = value
            return ''
        else:
            return value


@register.tag
def hitcounter(parser, token):
    bits = token.split_contents()
    obj = bits[1]
    as_var = None
    if len(bits) == 4:
        as_var = bits[3]

    return HitCounterNode(obj, as_var)
