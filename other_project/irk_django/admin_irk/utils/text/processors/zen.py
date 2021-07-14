# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from irk.utils.text import formatters
from irk.utils.text.processors.base import Processor

processor = Processor()

processor.add_simple_formatter('b', '<strong>%(value)s</strong>')
processor.add_simple_formatter('i', '<em>%(value)s</em>')
processor.add_simple_formatter('u', '<u>%(value)s</u>')
processor.add_simple_formatter('s', '<del>%(value)s</del>')
processor.add_simple_formatter('small', '<small>%(value)s</small>')
processor.add_simple_formatter('sup', '<sup>%(value)s</sup>')
processor.add_simple_formatter('q', '<blockquote>%(value)s</blockquote>', strip=True)
processor.add_simple_formatter('h2', '<h2>%(value)s</h2>', strip=True, render_embedded=False)
processor.add_simple_formatter('h3', '<h3>%(value)s</h3>', strip=True, render_embedded=False)
processor.add_simple_formatter('cite', '<div class="the-thought"><div>%(value)s</div></div>', strip=True)
processor.add_simple_formatter('list', '<ul>%(value)s</ul>', transform_newlines=False, strip=True)
processor.add_simple_formatter('*', '<li>%(value)s</li>', newline_closes=True, same_tag_closes=True, strip=True)
processor.add_simple_formatter('nbsp', '&nbsp;', strip=False, standalone=True)

processor.add_formatter(
    'url', formatters.bb.url_formatter, replace_links=False, replace_cosmetic=True, replace_smiles=False
)
processor.add_formatter(
    'email', formatters.bb.email_formatter, replace_links=False, replace_cosmetic=False, replace_smiles=False
)
processor.add_formatter(
    'image', formatters.zen.ImageFormatter(), standalone=True, replace_links=False, replace_cosmetic=False,
    replace_smiles=False
)
# processor.add_formatter(
#     'images', formatters.zen.images_formatter, standalone=True, replace_links=False, replace_cosmetic=False,
#     replace_smiles=False
# )
