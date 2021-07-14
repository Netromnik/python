# -*- coding: utf-8 -*-

import binascii
import logging
import re

import bleach

from irk.utils.text.formatters.bb import url_re


logger = logging.getLogger(__name__)

QUOTES_RE_0 = re.compile(u'((?s).*)')
QUOTES_RE_1 = re.compile(ur'''([\s!\]|#'"\/(;+-])"([^">]*)([^\s"(|])"([^\w])''', re.I | re.S | re.U)
QUOTES_RE_2 = re.compile(ur'«[^»]*«')
QUOTES_RE_3 = re.compile(u'«([^»]*)«([^»]*)»')


def quotes_callback_1(match):
    return u'%s«%s%s»%s' % match.groups()


def quotes_callback_3(match):
    return u'«%s„%s“' % match.groups()


def replace_quotes_callback(text):
    text = u' %s ' % text.group(0).replace(u'«', '"').replace(u'»', '"').replace(u'„', '"').replace(u'“', '"')\
        .replace(u'”', '"')

    for _ in (0, 1, 2):
        text = QUOTES_RE_1.sub(quotes_callback_1, text)

    while re.findall(QUOTES_RE_2, text):
        text = re.sub(QUOTES_RE_3, quotes_callback_3, text, re.S | re.I)

    # Сначала мы добавили по одному пробелу, чтобы сработали кавычки в начале и конце текста.
    # Теперь мы убираем эти пробелы. Мы не можем сделать .strip(), потому что там может быть больше пробелов,
    # но нам нужно убрать только один, а остальные оставить.
    if text.startswith(' '):
        text = text[1:]
    if text.endswith(' '):
        text = text[:-1]

    return text


def replace_quotes(text):
    return re.sub(u'((?s).*)', replace_quotes_callback, text)


class TagOptions(object):
    tag_name = None                  #: The name of the tag, all lowercase.
    newline_closes = False           #: True if a newline should automatically close this tag.
    same_tag_closes = False          #: True if another start of the same tag should automatically close this tag.
    standalone = False               #: True if this tag does not have a closing tag.
    render_embedded = True           #: True if tags should be rendered inside this tag.
    transform_newlines = True        #: True if newlines should be converted to markup.
    transform_quotes = False  #: True - заменяем кавычки " на елочки и лапки
    escape_html = True               #: True if HTML characters (<, >, and &) should be escaped inside this tag.
    replace_links = True             #: True if URLs should be replaced with link markup inside this tag.
    replace_cosmetic = True          #: True if cosmetic replacements (elipses, dashes, etc.) should be performed inside this tag.
    replace_smiles = True
    strip = False                    #: True if leading and trailing whitespace should be stripped inside this tag.
    swallow_trailing_newline = False #: True if this tag should swallow the first trailing newline (i.e. for block elements).

    def __init__(self, tag_name, **kwargs):
        self.tag_name = tag_name
        for attr, value in list(kwargs.items()):
            setattr(self, attr, bool(value))


class Processor(object):

    TOKEN_TAG_START = 1
    TOKEN_TAG_END = 2
    TOKEN_NEWLINE = 3
    TOKEN_DATA = 4

    REPLACE_ESCAPE = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),
    )

    def __init__(self, newline='\n', normalize_newlines=True, escape_html=True, replace_links=True, replace_cosmetic=True,
                 replace_smiles=True, tag_opener='[', tag_closer=']'):
        self.tag_opener = tag_opener
        self.tag_closer = tag_closer
        self.newline = newline
        self.normalize_newlines = normalize_newlines
        self.recognized_tags = {}
        self._allowed_tags = set()  # Хранилище ключей из `self.recognized_tags` для быстрого поиска, разрешен ли тег
        self.escape_html = escape_html
        self.replace_cosmetic = replace_cosmetic
        self.replace_links = replace_links
        self.replace_smiles = replace_smiles

        self.cosmetics = set([
            ('--', u'—'),
            ('...', u'…'),
            ('(c)', u'©'),
            ('(reg)', u'®'),
            ('(tm)', u' ™'),
        ])

        self.smiles = {}

    def add_cosmetic(self, text, replacement):
        self.cosmetics.add((text, replacement))

    def add_smiles(self, smiles):
        for smile in smiles:
            token = '{{{{ smile-code-{0} }}}}'.format(smile.id)
            self.smiles[token] = smile

    def add_formatter(self, tag_name, render_func, **kwargs):
        """
        Installs a render function for the specified tag name. The render function
        should have the following signature:

            def render(tag_name, value, options, parent, context)

        The arguments are as follows:

            tag_name
                The name of the tag being rendered.
            value
                The context between start and end tags, or None for standalone tags.
                Whether this has been rendered depends on render_embedded tag option.
            options
                A dictionary of options specified on the opening tag.
            parent
                The parent TagOptions, if the tag is being rendered inside another tag,
                otherwise None.
            context
                The keyword argument dictionary passed into the format call.
        """
        options = TagOptions(tag_name.strip().lower(), **kwargs)
        self.recognized_tags[options.tag_name] = (render_func, options)
        self._allowed_tags.add(options.tag_name)

    def add_simple_formatter(self, tag_name, format_string, **kwargs):
        """
        Installs a formatter that takes the tag options dictionary, puts a value key
        in it, and uses it as a format dictionary to the given format string.
        """
        def _render(name, value, options, parent, context):
            fmt = {}
            if options:
                fmt.update(options)
            fmt.update({'value': value})
            return format_string % fmt
        self.add_formatter(tag_name, _render, **kwargs)

    def _replace(self, data, replacements):
        """
        Given a list of 2-tuples (find, repl) this function performs all
        replacements on the input and returns the result.
        """
        for find, repl in replacements:
            data = data.replace(find, repl)
        return data

    def _newline_tokenize(self, data):
        """
        Given a string that does not contain any tags, this function will
        return a list of NEWLINE and DATA tokens such that if you concatenate
        their data, you will have the original string.
        """

        parts = data.split('\n')
        tokens = []

        for num, part in enumerate(parts):
            if part:
                tokens.append((self.TOKEN_DATA, None, None, part))
            if num < (len(parts) - 1):
                tokens.append((self.TOKEN_NEWLINE, None, None, '\n'))
        return tokens

    def _parse_opts(self, data):
        bits = data.split()

        return bits[0].lower(), bits[1:]

    def _parse_tag(self, tag):
        """
        Given a tag string (characters enclosed by []), this function will
        parse any options and return a tuple of the form:
            (valid, tag_name, closer, options)
        """
        if (not tag.startswith(self.tag_opener)) or (not tag.endswith(self.tag_closer)) or ('\n' in tag) or ('\r' in tag):
            return (False, tag, False, None)
        tag_name = tag[1:-1].strip()  # [1:-1] - отрезаем начало и конец BB тега []
        if not tag_name:
            return (False, tag, False, None)
        closer = False
        opts = []
        if tag_name[0] == '/':
            tag_name = tag_name[1:]
            closer = True
        # Parse options inside the opening tag, if needed.
        if (('=' in tag_name) or (' ' in tag_name)) and not closer:
            tag_name, opts = self._parse_opts(tag_name)
        return (True, tag_name.strip().lower(), closer, opts)

    def tokenize(self, data):
        """
        Tokenizes the given string. A token is a 4-tuple of the form:

            (token_type, tag_name, tag_options, token_text)

            token_type
                One of: TOKEN_TAG_START, TOKEN_TAG_END, TOKEN_NEWLINE, TOKEN_DATA
            tag_name
                The name of the tag if token_type=TOKEN_TAG_*, otherwise None
            tag_options
                A dictionary of options specified for TOKEN_TAG_START, otherwise None
            token_text
                The original token text
        """
        if self.normalize_newlines:
            data = data.replace('\r\n', '\n').replace('\r', '\n')
        pos = start = end = 0
        tokens = []
        while pos < len(data):
            start = data.find(self.tag_opener, pos)
            if start >= pos:
                # Check to see if there was data between this start and the last end.
                if start > pos:
                    tl = self._newline_tokenize(data[pos:start])
                    tokens.extend(tl)
                end = data.find(self.tag_closer, start)
                # Check to see if another tag opens before this one closes.
                new_check = data.find(self.tag_opener, start + 1)  # 1 в конце — это len(self.tag_opener)
                if 0 < new_check < end:
                    tokens.extend(self._newline_tokenize(data[start:new_check]))
                    pos = new_check
                elif end > start:
                    tag = data[start:end + 1]  # 1 в конце — это len(self.tag_closer)
                    valid, tag_name, closer, opts = self._parse_tag(tag)
                    # Make sure this is a well-formed, recognized tag, otherwise it's just data.
                    if valid and tag_name in self._allowed_tags:
                        if closer:
                            tokens.append((self.TOKEN_TAG_END, tag_name, None, tag))
                        else:
                            tokens.append((self.TOKEN_TAG_START, tag_name, opts, tag))
                    elif valid and tag_name not in self._allowed_tags:
                        # If we found a valid (but unrecognized) tag, just drop it.
                        pass
                    else:
                        tokens.extend(self._newline_tokenize(tag))
                    pos = end + 1  # 1 в конце — это len(self.tag_closer)
                else:
                    # An unmatched [
                    try:
                        last_token = list(tokens[-1])
                    except IndexError:
                        pass  # Текст начинается с [
                    else:
                        last_token[3] += self.tag_opener
                        tokens[-1] = tuple(last_token)
                        pos += sum(len(t[3]) for t in tokens)

                    break
            else:
                # No more tags left to parse.
                break

        if pos < len(data):
            tl = self._newline_tokenize(data[pos:])
            tokens.extend(tl)

        return tokens

    def _find_closing_token(self, tag, tokens, pos):
        """
        Given the current tag options, a list of tokens, and the current position
        in the token list, this function will find the position of the closing token
        associated with the specified tag. This may be a closing tag, a newline, or
        simply the end of the list (to ensure tags are closed). This function should
        return a tuple of the form (end_pos, consume), where consume should indicate
        whether the ending token should be consumed or not.
        """
        embed_count = 0
        while pos < len(tokens):
            token_type, tag_name, tag_opts, token_text = tokens[pos]
            if token_type == self.TOKEN_NEWLINE and tag.newline_closes:
                # If for some crazy reason there are embedded tags that both close on newline,
                # the first newline will automatically close all those nested tags.
                return pos, True
            elif token_type == self.TOKEN_TAG_START and tag_name == tag.tag_name:
                if tag.same_tag_closes:
                    return pos, False
                if tag.render_embedded:
                    embed_count += 1
            elif token_type == self.TOKEN_TAG_END and tag_name == tag.tag_name:
                if embed_count > 0:
                    embed_count -= 1
                else:
                    return pos, True
            pos += 1
        return pos, True

    def _transform(self, data, escape_html, replace_links, replace_cosmetic, replace_smiles):
        """
        Transforms the input string based on the options specified, taking into account
        whether the option is enabled globally for this parser.
        """
        url_matches = {}
        if self.replace_links and replace_links:
            # If we're replacing links in the text (i.e. not those in [url] tags) then we need to be
            # careful to pull them out before doing any escaping or cosmetic replacement.
            pos = 0
            while True:
                match = url_re.search(data, pos)
                if not match:
                    break

                # Тупой хак, чтобы не портился HTML, которого по идее не должно вообще никогда быть, но он есть
                # Смотрим текст вокруг ссылки и не заменяем ссылку, если она находится внутри src="" или href=""
                start, end = match.span()
                before_start = data[start-6:start]
                try:
                    after_end = data[end]
                except IndexError:
                    after_end = None

                # Нет смысла проверять начало HTML атрибута, если он не заканчивается кавычкой
                if after_end == '\'' or after_end == '"':

                    if before_start == 'href="' or before_start == 'href=\'':
                        pos = end - 1
                        continue

                    before_start = before_start[1:]
                    if before_start == 'src="' or before_start == 'src=\'':
                        pos = end - 1
                        continue

                # Replace any link with a token that we can substitute back in after replacements.
                token = '{{{{ code-link-{0} }}}}'.format(binascii.hexlify(match.group(0).encode('utf-8')))
                url_matches[token] = bleach.linkify(match.group(0))
                start, end = match.span()
                data = data[:start] + token + data[end:]
                # To be perfectly accurate, this should probably be len(data[:start] + token), but
                # start will work, because the token itself won't match as a URL.
                pos = start

        if self.replace_smiles and replace_smiles:
            for token, smile in sorted(self.smiles.items()):
                data = data.replace(smile.code, token)

        if self.escape_html and escape_html:
            data = self._replace(data, self.REPLACE_ESCAPE)

        if self.replace_cosmetic and replace_cosmetic:
            data = self._replace(data, self.cosmetics)

        # Now put the replaced links back in the text.
        for token, replacement in url_matches.items():
            data = data.replace(token, replacement)

        if self.replace_smiles and replace_smiles:
            for token, smile in self.smiles.items():
                data = data.replace(token, unicode(smile))

        return data

    def _format_tokens(self, tokens, parent, **context):
        idx = 0
        formatted = []
        tokens_len = len(tokens)

        while idx < tokens_len:
            token_type, tag_name, tag_opts, token_text = tokens[idx]
            if token_type == self.TOKEN_TAG_START:
                render_func, tag = self.recognized_tags[tag_name]
                if tag.standalone:
                    try:
                        formatted.append(render_func(tag_name, None, tag_opts, parent, context))
                    except:
                        # отладим
                        import traceback
                        traceback.print_stack()
                        logger.exception('Got an exception while processing BB code `{0}` with options {1}'.format(tag_name, tag_opts))
                else:
                    # First, find the extent of this tag's tokens.
                    end, consume = self._find_closing_token(tag, tokens, idx + 1)
                    subtokens = tokens[idx + 1:end]
                    # If the end tag should not be consumed, back up one (after grabbing the subtokens).
                    if not consume:
                        end = end - 1
                    if tag.render_embedded:
                        # This tag renders embedded tags, simply recurse.
                        inner = self._format_tokens(subtokens, tag, **context)
                    else:
                        # Otherwise, just concatenate all the token text.
                        inner = self._transform(''.join([t[3] for t in subtokens]), tag.escape_html, tag.replace_links, tag.replace_cosmetic, tag.replace_smiles)
                    # Strip and replace newlines, if necessary.
                    if tag.strip:
                        inner = inner.strip()
                    if tag.transform_newlines:
                        inner = inner.replace('\n', self.newline)

                    # Append the rendered contents.
                    try:
                        formatted.append(render_func(tag_name, inner, tag_opts, parent, context))
                    except:
                        logger.exception('Got an exception while processing BB code `{0}` with options {1}'.format(tag_name, tag_opts))

                    # If the tag should swallow the first trailing newline, check the token after the closing token.
                    if tag.swallow_trailing_newline:
                        next_pos = end + 1
                        if next_pos < tokens_len and tokens[next_pos][0] == self.TOKEN_NEWLINE:
                            end = next_pos
                    # Skip to the end tag.
                    idx = end
            elif token_type == self.TOKEN_NEWLINE:
                # If this is a top-level newline, replace it. Otherwise, it will be replaced (if necessary) by the code above.
                formatted.append(self.newline if parent is None else token_text)
            elif token_type == self.TOKEN_DATA:

                escape = context.get('escape_html')
                if escape is None:
                    escape = self.escape_html if parent is None else parent.escape_html

                links = context.get('replace_links')
                if links is None:
                    links = self.replace_links if parent is None else parent.replace_links

                smiles = context.get('replace_smiles')
                if smiles is None:
                    smiles = self.replace_smiles if parent is None else parent.replace_smiles

                cosmetic = self.replace_cosmetic if parent is None else parent.replace_cosmetic

                formatted.append(self._transform(token_text, escape, links, cosmetic, smiles))
            idx += 1
        return ''.join(formatted)

    def format(self, data, **context):
        """
        Formats the input text using any installed renderers.
        """

        data = replace_quotes(data)
        strip_bb_codes = context.pop('strip_bb_codes', False)
        if strip_bb_codes:
            data = self.strip_bb_codes(data)

        tokens = self.tokenize(data)

        return self._format_tokens(tokens, None, **context)

    def strip(self, data, strip_newlines=False):
        """
        Strips out any tags from the input text, using the same tokenization as the formatter.
        """
        text = []
        for token_type, tag_name, tag_opts, token_text in self.tokenize(data):
            if token_type == self.TOKEN_DATA:
                text.append(token_text)
            elif token_type == self.TOKEN_NEWLINE and not strip_newlines:
                text.append(token_text)
        return ''.join(text)

    @staticmethod
    def strip_bb_codes(data):
        return re.sub('\[.*?\]', '', data)

    def validate(self, data):
        """Валидатор ошибок с BB-кодами

        Разбивает текст на токены и проверяет, что все BB коды имеют открывающие и закрывающие теги"""

        queue = []
        tokens = self.tokenize(data)
        errors = []

        idx = 0
        tokens_len = len(tokens)


        def get_token_context(idx):
            result = []
            for token_type, tag_name, tag_opts, token_text in tokens[idx-5:idx+6]:
                result.append(token_text)

            return ''.join(result)

        while idx < tokens_len:
            token_type, tag_name, tag_opts, token_text = tokens[idx]

            if token_type == self.TOKEN_TAG_START:
                render_func, tag = self.recognized_tags[tag_name]
                if tag.standalone:
                    idx += 1
                    continue

                queue.append(idx)

            elif token_type == self.TOKEN_TAG_END:
                matched = False
                for item in queue[::-1]:
                    if tag_name != tokens[item][1]:
                        errors.append([self.TOKEN_TAG_START, tokens[item][3], get_token_context(item)])
                    else:
                        matched = True
                        break

                if not matched:
                    errors.append([self.TOKEN_TAG_END, token_text, get_token_context(idx)])

                queue.pop()

            idx += 1

        for item in queue:
            token_text = tokens[item][3]
            errors.append([self.TOKEN_TAG_END if token_text.startswith('[/') else self.TOKEN_TAG_START, token_text,
                           get_token_context(item)])

        return errors
