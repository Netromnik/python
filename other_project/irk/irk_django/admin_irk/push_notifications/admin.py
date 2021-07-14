# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse

from irk.utils.decorators import options
from irk.utils.files.admin import admin_media_static
from irk.utils.http import ajax_request

from irk.push_notifications import models
from irk.push_notifications import forms
from irk.push_notifications.tasks import send_message_for_all_task


@admin.register(models.Device)
class DeviceAdmin(admin.ModelAdmin):
    form = forms.DeviceAdminForm

    @admin_media_static
    class Media(object):
        css = {'all': ('css/admin.css', )}
        js = ('js/apps-js/admin.js', )


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'link', 'created', 'sent', 'send_message_link']
    form = forms.MessageAdminForm

    @admin_media_static
    class Media(object):
        css = {'all': ('css/admin.css',)}
        js = ('js/apps-js/admin.js', 'push_notifications/js/admin.js')

    def get_urls(self):
        urls = [
            url(r'^send_message/$', self.admin_site.admin_view(self._send_message), name='push_notifications_send'),
        ] + super(MessageAdmin, self).get_urls()

        return urls

    def save_model(self, request, obj, form, change):
        super(MessageAdmin, self).save_model(request, obj, form, change)

    @options(allow_tags=True, short_description=u'Отправка')
    def send_message_link(self, obj):
        """Ссылка для отправки сообщения"""

        return '<a class="j-notification-message-push" href="{}" data-message-id="{}">отправить</a>'.format(
            reverse('admin:push_notifications_send'),
            obj.id
        )

    @staticmethod
    @ajax_request
    def _send_message(request):
        """Отправка сообщения"""

        message_id = request.json.get('message_id')
        if not message_id:
            return {'ok': False, 'msg': u'Не указан id сообщения'}

        send_message_for_all_task.delay(message_id)

        return {'ok': True, 'msg': u'Сообщение отправлено'}


@admin.register(models.Distribution)
class DistributionAdmin(admin.ModelAdmin):
    pass
