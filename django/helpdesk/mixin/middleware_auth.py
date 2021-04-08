from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponseRedirect

from django.middleware.security import SecurityMiddleware
class CustomUserIsAuthenticationMiddleware(MiddlewareMixin):
    """
    Этот миддвере предназначенн для вылидации только авторизированных пользователей
    """

    def process_request(self, request):
        path = request.path.lstrip("/")
        if (path == 'admin/' or path == 'admin/login/' ):
            return
        if (not request.user.is_authenticated and (request.path != settings.LOGIN_URL )):
            return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))