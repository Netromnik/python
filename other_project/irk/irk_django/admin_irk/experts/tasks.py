# -*- coding: utf-8 -*-

from irk.utils.tasks.helpers import task
from irk.utils.notifications import tpl_notify
from irk.experts.models import Subscriber


@task(max_retries=1, ignore_result=True)
def expert_subscription_send(expert_id):
    """Рассылка уведомлений об ответе на вопросы конференции"""

    subscribers = Subscriber.objects.filter(expert_id=expert_id).prefetch_related('expert')

    for subscriber in subscribers:
        tpl_notify(u"Опубликованы ответы на вопросы в пресс-конференции {0} «IRK.ru»".format(subscriber.expert.title),
                   "experts/notif/subscriber.html", {'subscriber': subscriber}, emails=[subscriber.email, ])
        subscriber.delete()
