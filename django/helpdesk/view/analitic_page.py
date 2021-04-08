from django.shortcuts import render,Http404
from fsm.models import Task,Queue
import datetime
import django_tables2 as tables
from django.contrib.auth.models import User
from .table_class.common import AdminTask
from table_api.models import AnaliticTable

class AnaliticTable_D(tables.Table):
    class_id = "table-d"
    date = tables.Column(verbose_name="")
    reopen = tables.Column(verbose_name="Переоткрытые")
    open = tables.Column(verbose_name="Открытые")
    work = tables.Column(verbose_name="В работе")
    close = tables.Column(verbose_name="Закрытые")
    solve = tables.Column(verbose_name="решены")
    class Meta:
        attrs = {"thead":{
                     "id":"table"
                 }}


class AnaliticTable_W(tables.Table):
    class_id = "table-w"
    date = tables.Column(verbose_name="")
    reopen = tables.Column(verbose_name="Переоткрытые")
    open = tables.Column(verbose_name="Открытые")
    work = tables.Column(verbose_name="В работе")
    close = tables.Column(verbose_name="Закрытые")
    solve = tables.Column(verbose_name="решены")



class UserScopeTable_W(tables.Table):
    class_id = "table-user"
    user = tables.Column(verbose_name="Имя пользователя")
    raiting = tables.Column(verbose_name="Рейтинг")
    work = tables.Column(verbose_name="В работе")


def bd_count(q,data)->dict:
    return {
    "date": data.strftime("%d/%m/%Y"),
    "open": q.filter(state='Открыта').count(),
    "reopen": q.filter(state='Переоткрыта').count(),
    "work": q.filter(state='Ваполняется').count(),
    "solve": q.filter(state='Решена').count(),
    "close": q.filter(state='Закрыта').count(),
    }


def admin_analitic(request):
    user = request.user
    """ view function for sales app """
    if not ( user.is_superuser or user.is_staff):
        raise Http404
    date = datetime.datetime.today()
    # read data
    df = AnaliticTable.object.filter(groups__in=user.groups.all())
    ## месяц
    days_year = []
    date_start = date.replace(day=1)
    for i in range(31):
        q = df.filter(date_create__year=date.year, date_create__month=date.month, date_create__day=date_start.day + i)
        days_year.append(bd_count(q,data=date_start.replace(day=date_start.day + i)))

    # ## Неделя
    # days = []
    # date_start = date.replace(day=date.day - date.weekday())
    # for  i in range(7):
    #     q = df.filter(data_create__year=date.year, data_create__month=date.month,data_create__day=date_start.day+i)
    #     days.append(bd_count(q,data=date_start.replace(day=date_start.day + i)))
    ## create scope raiting
    scope = []
    # user =
    user_pk = list(set( [ u.pk for u in User.objects.filter(groups__in=set(user.groups.all())).order_by('pk')]))
    for g_user in  User.objects.filter(pk__in=user_pk):
            scope.append(
                { "user":g_user.get_full_name(),
                           "raiting": Task.statistic_data_manager.get_raiting(g_user),
                           "work":Task.object.filter(responsible= user,state="Ваполняется").count()
                })

    q = Queue.objects.filter(gr__in = user.groups.all(),parent=None)
    q |= Queue.objects.filter(parent__in=q)
    if date.month <2:
        admin_table = Task.object.filter(queue__in=q, data_create__year=date.year,
                                         data_create__month__gte=12, )
    else:
        admin_table = Task.object.filter(queue__in=q,data_create__year=date.year, data_create__month__gte=date.month-2,)

    context = {
        # 'table_week': AnaliticTable_D(days),
        'table_month': AnaliticTable_W(days_year),
        'user_scope':UserScopeTable_W(scope),
        'admin_table':AdminTask(admin_table)
               }
    return render(request, 'locations/sticstic_data.html', context=context)
