# -*- coding: utf-8 -*-

from django.conf import settings

# Список объектов, для которых могут храниться счетчики просмотров
# Ключ: название модели, вида `app_name.model_name`
# Значение: название поля модели, в которое будет сохраняться значение просмотров
COUNTABLE_OBJECTS = {
    'news.news': 'views_cnt',
    'news.article': 'views_cnt',
    'news.tildaarticle': 'views_cnt',
    'news.photo': 'views_cnt',
    'news.video': 'views_cnt',
    'news.infographic': 'views_cnt',
    'news.podcast': 'views_cnt',
    'obed.article': 'views_cnt',
    'obed.review': 'views_cnt',
    'afisha.review': 'views_cnt',
    'tourism.tour': 'views_cnt',
    'blogs.blogentry': 'view_cnt',
    'testing.test': 'views_cnt',
}

# Время, в которое несколько хитов пользователя считаются за один
USER_KEY_EXPIRE = getattr(settings, 'HIT_LOG_EXPIRE', 60 * 60 * 24)

# Настройки базы redis для этого приложения
REDIS_DB = settings.REDIS.get('hitcounters', {
    'HOST': 'localhost',
    'DB': 5
})


# Количество секунд добавляемое к статистике времени чтения материала на один запрос фротенда
READ_TIME_INTERVAL = 5
