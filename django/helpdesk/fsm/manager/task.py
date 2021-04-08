from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class CustomManegerTaskStatistic(models.Manager):
    ## return stat +!
    ## return is_avtor Task +
    ## return is use for stream
    ## return is use for asignet
    def stats_for_admin(self,user:User)->list:
        list_req = []
        own_q = self.filter(owner=user)
        if own_q.count() != 0:
            obj = {
                "name": "Созданные вами",
                "all:": own_q.count(),
                "open": own_q.filter(state='Открыта').count(),
                "reopen": own_q.filter(state='Переоткрыта').count(),
                "work": own_q.filter(state='Ваполняется').count(),
                "solve": own_q.filter(state='Решена').count(),
                "close": own_q.filter(state='Закрыта').count(),
                "err": own_q.filter(state='Ошибка').count(),
            }
            list_req.append(obj)
        return list_req

    def  stats(self,user:User)->list:
        list_req = []
        own_q = self.filter(owner=user)
        resp_q = self.filter(responsible=user)
        if own_q.count() !=0:
            obj = {
            "name":"Созданные вами",
            "all:":own_q.count(),
            "open":own_q.filter(state='Открыта').count(),
            "reopen":own_q.filter(state='Переоткрыта').count(),
            "work":own_q.filter(state='Ваполняется').count(),
            "solve":own_q.filter(state='Решена').count(),
            "close":own_q.filter(state='Закрыта').count(),
            "err":own_q.filter(state='Ошибка').count(),
                }
            list_req.append(obj)

        if resp_q.count() != 0:
            obj2 = {
            "name":"Под вашим управлением",
            "all:":resp_q.count(),
            "open":resp_q.filter(state='Открыта').count(),
            "reopen":own_q.filter(state='Переоткрыта').count(),
            "work":resp_q.filter(state='Ваполняется').count(),
            "solve":resp_q.filter(state='Решена').count(),
            "close":resp_q.filter(state='Закрыта').count(),
            "err":resp_q.filter(state='Ошибка').count(),
                }
            list_req.append(obj2)
        return list_req
    def get_raiting(self,user:User):
        resp_q = self.filter(responsible=user)
        
        raiting = resp_q.exclude(raiting=-1).aggregate(Avg("raiting"))['raiting__avg'] 
        if raiting == None:
            return 0
        else:
            return raiting*10//1/10

    def is_avtor(self,user):
        return self.filter(autors=user)
