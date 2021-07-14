# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view, obj=None):
        if getattr(view, 'skip_authentication', False):
            return True

        return bool(request.auth)
