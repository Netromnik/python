# -*- coding: utf-8 -*-

# Типы рейтинга
RATING_TYPES = {
    'like': (1,),  # Нравится!
    'like_wedding': (1,),  # Нравится!
    'binary': (-1, 1),  # Не нравится / нравится
    'range10': range(1, 11),  # Значения от 1 до 10
}

# Объекты, за которые можно голосовать
RATEABLE_OBJECTS = {
    'afisha.Event': {
        'type': 'range10',
    },
    'comments.Comment': {
        'type': 'binary',
        'user_fk': 'user',
    },
    'experts.Expert': {
        'type': 'like',
        'user_fk': 'user',
    },
    'phones.Firms': {
        'type': 'range10',
    },
    'contests.Participant': {
        'type': 'like',
        # Для всех фотоконкурсов решили убрать анонимусов
        'anonymous': False,
    },
    'blogs.BlogEntry': {
        'type': 'like',
        'template': 'ratings/widgets/results/like_blogs.html',
        'user_fk': 'author',
    },
    'news.Infographic': {
        'type': 'like',
        'template': 'ratings/widgets/results/like_blogs.html',
    },
}

COOKIE_NAME = 'rl'

# Минимальное число голосов для участия в рейтинге по методу Байеса
BAYES_MINIMUM_VOTES = 10
