# -*- coding: utf-8 -*

from django.utils.functional import cached_property
from django.conf import settings

from irk.options.models import Site


class CurrentSite(object):
    """Хелпер, содержащий информацию про текущий раздел"""

    TYPE_WWW = 1  # Запрос на сайт

    # Соответствие типа раздела к домену
    DOMAINS = {
        TYPE_WWW: 'www',
    }

    section = 'www'  # Тип раздела (html,мобильный)
    request_type = TYPE_WWW  # Тип раздела ID

    def __init__(self, request):
        self.request = request

    @cached_property
    def site(self):
        """
        Получить объект, представляющий раздел сайта

        Сделан как cached_property, чтобы не делать sql-запрос, пока кто-то явно не обратится
        к `request.csite`
        """

        site = Site.objects \
            .extra(where=['`url` != "" AND INSTR("%s", `url`) between 1 and 2'], params=[self.request.path, ]) \
            .first()

        if not site:
            site = Site.objects.get(slugs='home')

        return site

    def is_mobile_site(self):
        """Является ли этот запрос на мобильный сайт"""

        return False

    def is_mobile_device(self):
        """Запрос сделан с мобильного устройства"""

        return False

    def is_logout_path(self):
        """Запрос на ссылку деавторизации"""

        return self.request.path == self.LOGOUT_URL

    def is_admin_path(self):
        """Запрос в админку"""

        return self.request.path.startswith('/adm/')  # TODO: reverse, вынести в атрибут класса

    def is_home_path(self):
        """Запрос на главную страницу"""

        return self.request.path in ('/home/', '/')  # TODO: reverse, вынести в атрибут класса

    def redirect_to_mobile(self):
        """Нужно ли переадресовывать пользователя на мобильную версию сайта"""

        return False

    def get_request_root_urlconf(self):
        """Корневой urlconf для текущего запроса"""

        return settings.ROOT_URLCONF

    def get_section_url(self, name, domain_only=False):
        """Возвращает полный url раздела или урл соответствующего сайта"""

        url = getattr(self, "%s_HOST" % name.upper(), None)
        if url:
            return url

        host = "%s.%s" % (self.DOMAINS.get(self.request_type), settings.BASE_HOST)
        if domain_only:
            return host

        try:
            url = Site.objects.get_by_domain(name).get_url()
        except AttributeError:
            url = ''

        return '%s%s' % (host, url)

    @classmethod
    def get_site_url(cls, name, domain_only):
        """Ссылка на раздел"""

        domain_type = getattr(cls, 'TYPE_%s' % name.upper(), None)
        # Запрашивается домен www
        if domain_type:
            return '%s.%s' % (cls.DOMAINS.get(domain_type), settings.BASE_HOST)

        # Запрос сайта
        domain = '%s.%s' % (cls.DOMAINS.get(cls.TYPE_WWW), settings.BASE_HOST)
        if domain_only:
            return domain

    def is_force_www(self):
        """Отображать ли принудительно полную версию сайта"""

        # Всегда отображать полную версию
        return True

    def __getattr__(self, name):

        # Если запрос типа DOMAIN_HOST (MOBILE,WWW,WIDGETS)
        # Возвращаем полный адрес хоста
        if name.endswith("_HOST"):
            domain_type = getattr(self, "TYPE_%s" % name.replace('_HOST', ''), None)
            if domain_type:
                return "%s.%s" % (self.DOMAINS.get(domain_type), settings.BASE_HOST)

        return getattr(self.site, name)

    def __int__(self):
        return self.site.pk


def url_alias(context):
    """Возвращает соответствующий URL для мобильной/полной версии сайта"""

    request = context.get('request')
    # TODO: проверка, что `request` доступен в контексте

    # Если это мобильная часть, то пробуем  перейти на соответствующую часть основного сайта
    if not request.csite.is_home_path() and request.csite.is_mobile_site():
        # для гида делаем отдельно
        if request.path.startswith("/afisha/guide/"):  # TODO: reverse
            path_data = request.path.strip("/").split("/")
            path_data.pop(0)
            if len(path_data) == 3:
                path_data.pop(1)
            return "/%s/" % ("/".join(path_data))
        elif request.path == '/feedback/':  # TODO: reverse
            return '/about/feedback/'  # TODO: reverse
        else:
            return request.path

    return '/'


def site_url(url):
    # TODO: docstring
    try:
        return Site.objects.all().extra(where=['`url` != "" AND INSTR("%s", `url`) between 1 and 2'], params=[url, ])[0]
    except IndexError:
        raise Site.DoesNotExist()
