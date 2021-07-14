# -*- coding: utf-8 -*-

"""Задачи celery"""

from irk.utils.tasks.helpers import make_command_task


profiles_clean = make_command_task('profiles_clean')

profiles_unban = make_command_task('profiles_unban')

profiles_ban_dogs = make_command_task('profiles_ban_dogs')

profiles_process_bounces = make_command_task('profiles_process_bounces')
