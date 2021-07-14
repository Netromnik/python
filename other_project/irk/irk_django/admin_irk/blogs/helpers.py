# -*- coding: utf-8 -*-

import re


def parse_caption(text):
    """Получение первого параграфа текста для записи блогов"""

    CAPTION_LINE_RE = re.compile(r'^\n*([^\n]+)\n.*$', re.S)
    text = re.sub(ur'\[(.*?)\]', '', text).strip()

    return re.sub(CAPTION_LINE_RE, r'\1', text)
