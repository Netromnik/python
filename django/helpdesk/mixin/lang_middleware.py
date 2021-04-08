from django.middleware.common import MiddlewareMixin
class ForceDefaultLanguageMiddleware(MiddlewareMixin):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies

    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """

    def process_request(self, request):
        # request.META["HTTP_ACCEPT_LANGUAGE"] ="en-US,en;q=0.5"
        request.META["HTTP_ACCEPT_LANGUAGE"] ="ru-RU,ru;q=0.5"
