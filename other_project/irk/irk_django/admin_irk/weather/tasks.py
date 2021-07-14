# -*- coding: utf-8 -*-

from django.core.management import call_command

from irk.utils.tasks.helpers import make_command_task, task


@task(ignore_result=True, max_retries=3)
def openweathermap_current():
    call_command('weather_openweathermap', current=True)


@task(ignore_result=True, max_retries=3)
def openweathermap_detailed():
    call_command('weather_openweathermap', detailed=True)


weather_grabber_maps = make_command_task('weather_grabber_maps')
