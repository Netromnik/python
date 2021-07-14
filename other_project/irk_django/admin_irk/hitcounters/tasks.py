# -*- coding: utf-8 -*-

"""Задачи celery"""


from irk.utils.tasks.helpers import make_command_task


hitcounters_update_values = make_command_task('hitcounters_update_values')
hitcounters_by_day_update = make_command_task('hitcounters_by_day_update')
hitcounters_update_scroll_depth = make_command_task('hitcounters_update_scroll_depth')
