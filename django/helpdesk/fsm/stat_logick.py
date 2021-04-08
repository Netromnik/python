# from django.contrib.auth.models import User
from .models import STATES_list as STATES
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse

class Button:
    type =  "info"
    href  = ""
    name =  ""

def dispath(stat:str,type:str,task_pk:int)->list:
    if stat == "Переоткрыта":
        stat = "Открыта"
    data = None
    if type == "owner":
        data = dispath_owner(stat,task_pk)
    elif type == "responsible" or stat == STATES[0]:
        data = dispath_responsible(stat,task_pk)
    return data

def dispath_owner(stat:str,task_pk:int)->list:
    button_list =[]
    if stat == STATES[0]:
        pass
    elif stat == STATES[1]:
        pass
    elif stat == STATES[2]:
        btn = Button()
        btn.name="Закрыть"
        btn.href=reverse("close_task",args=[task_pk,])
        btn.type="button btn-secondary"
        button_list.append(
            btn,
        )
    elif stat == STATES[3]:
        pass

    return button_list

def dispath_responsible(stat:str,task_pk:int):
    button_list =[]
    if stat == STATES[0]:
        """ Open task """

        btn = Button()
        btn.name="Принять"
        btn.href=reverse("start_task",args=[task_pk,])
        btn.type="button btn-secondary "
        button_list.append(
            btn,
        )
    elif stat == STATES[1]:
        """
        Proccess
            # re-open
            close
        """
        btn = Button()
        btn.name="Завершить"
        btn.href=reverse("successful_task",args=[task_pk,])
        btn.type="button btn-secondary"
        button_list.append(
            btn,
        )

        var = [
            # StatesBaseForm(
            #     button_name=["отказаться","Отказаться"],
            #     form_id="void-1",
            #     button_class="button btn-primary",
            #     hide_data="Open"
            # )
            # StatesBaseForm(
            #     button_name=["Переоткрыть", "Переоткрыть"],
            #     form_id="void-1",
            #     button_class="button btn-secondary",
            #     hide_data="Open"
            # ),
        ]

    elif stat == STATES[2]:
        """ Solve
          * re-open
         """
        pass

    elif stat == STATES[3]:
        """Переоткрыта"""
        btn = Button()
        btn.name="Принять"
        btn.href="void"
        btn.type="button btn-secondary"
        button_list.append(
            btn,
        )
    elif stat == STATES[3]:
        btn = Button()
        btn.name="Принять"
        btn.href=reverse("start_task",args=[task_pk,])
        btn.type="button btn-secondary"
        button_list.append(
            btn,
        )

    return button_list


