# -*- coding: utf-8 -*-

import logging

from irk.hitcounters.settings import COUNTABLE_OBJECTS


logger = logging.getLogger(__name__)


def get_hitcounter_info(obj):
    """ Возвращает тип и поле счетчика """

    opts = obj._meta

    obj_types = [unicode(opts)]
    if opts.parents:
        obj_types += map(lambda x: unicode(x._meta), opts.parents.keys())

    logger.debug('Seeking a countable model within %r' % obj_types)

    for obj_type in obj_types:
        if obj_type in COUNTABLE_OBJECTS:
            break
    else:
        logger.error('Got an unknown object %r #%r' % (repr(obj), obj.pk))
        return

    return {
        'obj_type': obj_type,
        'db_field': COUNTABLE_OBJECTS[obj_type],
    }
