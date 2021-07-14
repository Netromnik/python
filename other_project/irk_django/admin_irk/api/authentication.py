# -*- coding: utf-8 -*-

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from irk.api.models import Application


class ApplicationAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request._request.GET.get('token')

        try:
            app = Application.objects.get(access_token=token)
        except Application.DoesNotExist:
            return None

        return None, app


