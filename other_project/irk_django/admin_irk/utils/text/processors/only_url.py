# -*- coding: utf-8 -*-
"""
Текстовый процессор для обработки только тега url
"""

from __future__ import absolute_import, print_function, unicode_literals

from irk.utils.text import formatters
from irk.utils.text.processors.base import Processor

processor = Processor()
processor.add_formatter(
    'url', formatters.bb.url_formatter, replace_links=False, replace_cosmetic=True, replace_smiles=False
)
processor.add_simple_formatter('nbsp', '&nbsp;', strip=False, standalone=True)
