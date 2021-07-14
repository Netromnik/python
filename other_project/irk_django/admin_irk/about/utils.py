import contextlib
import datetime
import email.utils as email_utils
import locale
import os
import re
import shutil
import threading
import time
import types
from itertools import repeat
from math import ceil

# import chardet
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import ValidationError, validate_ipv4_address
from django.db import connection
from django.shortcuts import _get_queryset
from django.utils.encoding import DjangoUnicodeDecodeError
# from django.utils.text import force_unicode as fu
from pytils.numeral import choose_plural

from map.models import Cities
from options.models import Site

def inttoip(n):
    d = 256 * 256 * 256
    q = []
    while d > 0:
        m, n = divmod(n, d)
        q.append(str(m))
        d /= 256

    return '.'.join(q)

def tpl_notify(title, template, context, request=None, emails=(), sender=None, attachments=None):
    """Отправка E-mail сообщения пользователям

    Сообщение рендерится из шаблона"""

    context['ban_periods'] = settings.BAN_PERIODS
    if request:
        msg = render_to_string(template, context, request=request)
    else:
        msg = render_to_string(template, context)

    return notify(title, msg, emails, sender=sender, attachments=attachments)
