# -*- coding: utf-8 -*-

import locale
import re
import string

import phonenumbers
import simplejson

from django.template import Library, Node, Variable
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe
from django.conf import settings
from django.urls import reverse

from irk.utils.metrics import NewrelicTimingMetric
from irk.utils.text.processors.default import processor

locale.setlocale(locale.LC_ALL, '')


def do_typograph(text, params='title'):
    """Обработка типографом текста в шаблонах"""

    with NewrelicTimingMetric('Custom/Typograph'):
        text = force_unicode(text)
        params = map(string.strip, params.split(','))
        type_ = params[0]
        no_linebreaks = 'nolinebreaks' in params
        yes_linebreaks = 'linebreaks' in params

        kwargs = {}
        if type_ == 'title':
            kwargs['replace_links'] = False
            kwargs['replace_smiles'] = False
        elif type_ == 'admin':
            kwargs['escape_html'] = False

        if type_ not in ('title', 'admin', 'user'):
            raise ValueError()

        for param in params:
            # обрезка фоток в теге image
            if 'image' in param:
                kwargs['image'] = param.split('=')[1]

            # обрезка фоток в теге images
            if 'gallery' in param:
                kwargs['gallery'] = param.split('=')[1]

        # если в статье есть карточки, то включается особый режим типографа:
        # не делается linebreaks, который рвет разметку карточек. Вместо этого
        # linebreaks делается внутри форматтера бб-кода cards
        if '[cards' in text:
            no_linebreaks = True
        result = processor.format(text, **kwargs).strip()

        if type_ in ('title',):
            # Кажется, для этих типов ничего не надо делать больше с текстом
            if yes_linebreaks:
                result = linebreaks(result)
        else:
            if not no_linebreaks and type_ in ('user', 'admin') or yes_linebreaks:
                result = linebreaks(result)

        return mark_safe(result)


def price_format(value, arg):
    # TODO: docstring
    value = u"%.2f" % value
    value = value.replace(".", ",")

    return value


def do_truncate_words_to_str_length(text, num=200):
    """Обрезает строку, оставляя целые слова, общая длина которых не больше `num`"""

    num = int(num)

    if len(text) > num:
        values = text[:num].split()
        values.pop()
        text = ' '.join(values) + '...'

    return text


class TextRender(Node):
    """Обработка текста типографом

    TODO: обработка placeholders в тексте и замена их на значения из словаря data"""

    def __init__(self, variable, data):
        self.variable = Variable(variable)
        self.data = Variable(data)

    def render(self, context):
        text = self.variable.resolve(context)

        return do_typograph(text, 'user')


def do_text_render(parser, token):
    tag, variable, data = token.split_contents()

    return TextRender(variable, data)


class ClearClassesNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        output = self.nodelist.render(context)
        output = output.replace(' class=""', '')
        return output


def do_clearclasses(parser, token):
    """Удаляет из верстки пустые атрибуты class"""
    nodelist = parser.parse(('endclearclasses',))
    parser.delete_first_token()
    return ClearClassesNode(nodelist)


# TODO: переделать в декораторы
register = Library()
register.filter('price', price_format)
register.filter('typograf', do_typograph)
register.filter('truncate_words_to_str_length', do_truncate_words_to_str_length)
register.tag('text_render', do_text_render)
register.tag('clearclasses', do_clearclasses)


@register.filter
def json(data):
    # TODO: docstring
    return mark_safe(simplejson.dumps(data, ensure_ascii=False))


@register.filter
def tofloat(value):
    # TODO: docstring
    return str(value).replace(",", ".")


@register.filter
def float_point(value):
    # TODO: docstring
    return unicode(value).replace('.', ',')


@register.filter
def number_format(value, format="%d"):
    # TODO: docstring
    return locale.format(format, value, grouping=True)


@register.filter(safe=True)
def human_price(value, decimal_points=3, separator=u' '):
    """Фильтр, выводящий числовое значение, разбитое на разряды

    >>> human_price(100000)
    '100 000'
    >>> human_price(100000000)
    '100 000 000'
    """

    value = str(value)
    if len(value) <= decimal_points:
        return value

    parts = []
    while value:
        parts.append(value[-decimal_points:])
        value = value[:-decimal_points]

    parts.reverse()

    return separator.join(parts)


@register.filter
@stringfilter
def twitter_urlize(text):
    """Подсветка ссылок, юзернеймов и хэштегов"""

    def link(match):
        return u'<a href="%s">%s</a>%s' % (match.group(0).strip(),
            match.group(0)[:25].strip() if len(match.group(0)) > 25 else match.group(0).strip(), match.group(6))

    def list(match):
        return u'@<a href="http://twitter.com/%s">%s</a>' % (match.group(1), match.group(1))

    def username(match):
        return u'@<a href="http://twitter.com/%s">%s</a>' % (match.group(1), match.group(1))

    def hashtag(match):
        return u'%s<a href="http://twitter.com/search?q=%%23%s">#%s</a>' % (match.group(1), match.group(2),
                                                                            match.group(2))

    text = re.sub(r'\b(((https*\:\/\/)|www\.)[^\"\']+?)(([!?,.\)]+)?(\s|$))', link, text)
    text = re.sub(r'\B\@([a-zA-Z0-9_]{1,20}\/\w+)', list, text)
    text = re.sub(r'\B\@([a-zA-Z0-9_]{1,20})', username, text)
    text = re.sub(r'(\s*)\#(\w+)', hashtag, text)

    return text


class RuPhoneNumberMatcher(phonenumbers.PhoneNumberMatcher):
    def __init__(self, *args, **kwargs):
        super(RuPhoneNumberMatcher, self).__init__(*args, **kwargs)

        self._matches = []

        for raw_match in re.split(',|;', self.text):
            match = re.sub(r'\(.*?\)', '', raw_match)

            phone = self._find(match)
            if phone:
                self._matches.append(phone)
            else:
                try:
                    # Сначала вырезаем все в скобках, потом все не-числовые символы
                    phone = phonenumbers.parse(re.sub(r'[^\d]*', '', match), 'RU')
                except phonenumbers.NumberParseException:
                    continue
                self._matches.append(phonenumbers.PhoneNumberMatch(0, raw_match, phone))

    def _find(self, text, index=0):
        max_tries = 1024
        match = phonenumbers.phonenumbermatcher._PATTERN.search(text, index)
        while max_tries > 0 and match is not None:
            start = match.start()
            candidate = text[start:match.end()]

            candidate = self._trim_after_first_match(phonenumbers.phonenumbermatcher._SECOND_NUMBER_START_PATTERN,
                                                     candidate)

            match = self._extract_match(candidate, start)
            if match is not None:
                return match
                # Move along
            index = start + len(candidate)
            max_tries -= 1
            match = phonenumbers.phonenumbermatcher._PATTERN.search(text, index)

        return None

    def __iter__(self):
        for match in self._matches:
            yield match


@register.filter
def split_phones(text):
    """ Разбор строки на отдельные телефонные номера """

    for match in RuPhoneNumberMatcher(text, 'RU'):
        raw_string = re.sub(r'[^\d]*', '', match.raw_string)
        if raw_string.startswith('8800'):
            # Номера, начинающиеся на 8 800
            yield {
                'before': '',
                'link': raw_string,
                'text': phonenumbers.format_in_original_format(match.number, 'RU'),
                'after': '',
            }
        elif raw_string.startswith(('89', '+79')):
            # Мобильные телефоны
            yield {
                'before': '',
                'link': phonenumbers.format_number_for_mobile_dialing(match.number, 'RU', with_formatting=False),
                'text': phonenumbers.format_number_for_mobile_dialing(match.number, 'RU', with_formatting=True),
                'after': '',
            }
        else:
            yield {
                'before': '',
                'link': match.number.national_number,
                'text': match.raw_string,
                'after': '',
            }


@register.filter(is_safe=True)
def truncatesentences(value, arg):
    """
    Truncates a string after a certain number of sentences.

    Argument: Number of sentences to truncate after.
    """

    if value and int(arg) > 0:
        sentences = value.split('.')
        return '%s.' % '. '.join(sentences[:int(arg)])
    else:
        return ''


@register.filter
def truncatechars_until_sentence(value, arg):
    """
    Обрезать строку по количеству символов с учетом целостности предложения
    """

    try:
        length = int(arg)
    except ValueError:  # Invalid literal for int().
        return value

    if not value:
        return value

    # разобъем по предложениям (включая знаки окончания предложений)
    chunks = re.split(r"(?<=[.?!])\s", value)

    # теперь наберем в result те предложения, которые не переполняют

    # первое предложение всегда возвращается
    result = [chunks.pop(0)]

    while chunks:
        chunk = chunks.pop(0)

        # если добавление этого предложения переполнит чашу терпения,
        # то остановимся на том, что уже набрали
        if len(' '.join(result + [chunk])) > length:
            break
        result.append(chunk)

    return mark_safe(' '.join(result))


@register.filter
def clear_phones(text):
    """
    Оставляет в тексте только телефонные номера.

    >>> clear_phones(u'8 (902) 5 76-78-78 дялял, 23-15-48')
    >>> u'8 (902) 576-78-78, 23-15-48'
    """

    return re.sub(ur'[^\d,\(\)-]', u'', text).replace(',', ', ').replace('(', ' (').replace(')', ') ')


@register.filter
def int_to_text_with_sign(number):
    """
    Перевод числа в текст добавлением + для положительного числа и - с пробелом для отрицательного
    :type number: int
    :return: Число в текстовом виде
    :rtype: unicode
    """

    if number < 0:
        number = u'- {}'.format(abs(number))
    elif number > 0:
        number = u'+{}'.format(number)
    else:
        number = u'{}'.format(number)

    return number


@register.filter
def split_string(value, sep=','):
    """
    Разбить строку по разделителю sep, как метод split у строк.

        >>> split_string('123, 456, 789')
        >>> ['123', '456', '789']
    """

    if not isinstance(value, basestring):
        value = unicode(value)

    return [s.strip() for s in value.split(sep)]


@register.filter
def has_bb_code(value, bb_codes):
    """
    Проверяет наличие ББ кодов в value
    Можно проверять наличие нескольких бб-кодов просто перечисляя их через пробел.
    В этом случае функция вернет True, если все бб-коды есть в value

    :type value: str
    """

    return all(re.search(r'\[{}'.format(code.strip()), value) for code in re.split(r' |,', bb_codes) if code)


@register.simple_tag
def absolute_url(value, *args, **kwargs):
    """
    Пример использования:
        {% absolute_url 'news:news:index' %}
        {% absolute_url request.path %}
    """
    if '/' in value:
        return '{}{}'.format(settings.BASE_URL, value)
    else:
        return '{}{}'.format(settings.BASE_URL, reverse(value, args=args, kwargs=kwargs))
