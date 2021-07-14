# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import mimetypes
import os

from django.shortcuts import render

from irk.landings.forms import AuthResumeForm, AnonymousResumeForm
from irk.utils.notifications import tpl_notify
from irk.utils.http import JsonResponse


def resume(request):
    """Страница отправки резюме"""

    if request.user.is_authenticated:
        form_class = AuthResumeForm
    else:
        form_class = AnonymousResumeForm

    if request.POST:
        if request.is_ajax():
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()

                if instance.attach:
                    ext = os.path.splitext(instance.attach.file.name)[1]
                    mime_type = mimetypes.guess_type(instance.attach.file.name)[0]
                    attachment = [("file%s" % ext, instance.attach.file.read(), mime_type)]
                else:
                    attachment = None

                tpl_notify('Новое резюме от irk.ru', 'landings/notif/resume.html', {'resume': instance}, request,
                           emails=['vacancy@irk.ru'], attachments=attachment)
                return JsonResponse({'result': 'ok'})
            else:
                return JsonResponse({'result': 'error', 'errors': form.errors})
        return JsonResponse({'result': 'error'})
    context = {
        'form': form_class()
    }

    return render(request, 'landings/resume.html', context)
