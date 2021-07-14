# -*- coding: utf-8 -*-

# Классы материалов отображаемых в слайдере на главной афиши. У этих материалов должно быть поле is_announce
SLIDER_MATERIAL_CLASSES = ['Article', 'Review', 'Photo']


# Kassy.ru
KASSY_AGENT_ID = 'irk.ru'
KASSY_SECRET = '7fad3d93ada392aebc9aaae1778bcc11'
# подразделение, которому адресованы запросы
KASSY_DB = 'irk'

# Rambler.Kassa
RAMBLER_API_KEY = '60f94e9e-37e9-4952-92c5-fc225a13ef3d'
RAMBLER_CITY_ID = 6

# Kinomax
KINOMAX_CINEMA_IDS = ['irkutsk']
# Количество дат вперед для парсинга
KINOMAX_DAYS = 5

# Увеличить число материалов на главной афиши c 5 до 8
INDEX_EXTRA_MATERIAL = False

# Число материалов и событий подгружаемых аяксом по умолчанию
DEFAULT_EXTRA_AJAX_COUNT = 9

# Стоимость коммерческого размещения за одну дату в рублях
COMMERCIAL_EVENT_PRICE = 500

# Стоимость коммерческого размещения в карусели на главной за одни сутки в рублях
COMMERCIAL_EVENT_CAROUSEL_PRICE = 1000

# ID призмы проставляемой по умолчанию при добавлении коммерческого события
COMMERCIAL_EVENT_DEFAULT_PRISM = 1


# Количество дней показа 410 страницы для прошедших событий
PAST_EVENT_410_DAYS = 30
