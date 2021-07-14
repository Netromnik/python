# -*- coding: utf-8 -*-

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from irk.news.models import Flash, FlashBlock
from irk.utils.notifications import tpl_notify
from irk.news.permissions import get_flash_moderators
from irk.news.api.serializers import FlashCreateSerializer


class FlashCreate(CreateAPIView):
    serializer_class = FlashCreateSerializer
    model = Flash
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)

            if FlashBlock.objects.filter(pattern=serializer.object.username).count():
                return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

            self.object = serializer.save()
            headers = self.get_success_headers(serializer.data)

            result = Flash.objects.get(pk=self.object.id)

            tpl_notify(u'Добавлена народная новость', 'news/notif/flash/add.html', {'instance': result},
                       request, emails=get_flash_moderators().values_list('email', flat=True))

            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


flash_create = FlashCreate.as_view()
