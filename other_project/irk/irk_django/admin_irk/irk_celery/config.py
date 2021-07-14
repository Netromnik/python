from celery.schedules import crontab

# Спиок задач для очереди periodic

# Распределение задач по очередям происходит в CELERY_TASK_ROUTES. В основном
# почти все задачи из этого списка попадают в очередь periodic

# Из-за бага в Celery 4 не учитывается временная зона https://github.com/celery/celery/issues/4842
# Поэтому время указываем в UTC

PERIODIC_TASKS = [
    {'task': 'news_publish_scheduled', 'schedule': crontab()},
    {'task': 'scheduler_socpult', 'schedule': crontab()},
    # {'task': 'celery.backend_cleanup', 'schedule': crontab(0, 4)},
    {'task': 'grab_covid_data', 'schedule': crontab(0)},
    {'task': 'create_covid_cards', 'schedule': crontab(0, 0)},
    {'task': 'push_notifications_clean_devices', 'schedule': crontab(10, 2, 'sun')},
    {'task': 'afisha_hide_old_events', 'schedule': crontab(0, 7)},
    {'task': 'afisha_clean_cache', 'schedule': crontab(0, 2)},
    {'task': 'irk.afisha.tasks.run_kassy_grabber', 'schedule': crontab(0, '*/6')},
    {'task': 'irk.afisha.tasks.run_rambler_grabber', 'schedule': crontab(0)},
    # пока отключим - нужно перепроверить, похоже, он не работал раньше и теперь
    # ринулся работать - не заблокируют ли нас?
    # {'task': 'profiles_ban_dogs', 'schedule': crontab(0, '*/6')},
    # {'task': 'externals_instagram_by_tags', 'schedule': crontab(0, '*/20')},
    {'task': 'news_disable_comments', 'schedule': crontab('*/10')},
    {'task': 'news_irkdtp_grabber', 'schedule': crontab('*/20')},
    # {'task': 'contests_instagram', 'schedule': crontab('*/30')},
    {'task': 'news_twitter_grabber', 'schedule': crontab('*/5')},
    {'task': 'news_send_daily_distribution', 'schedule': crontab(0, 20)},
    {'task': 'news_send_weekly_distribution', 'schedule': crontab(0, 16, 'sat')},
    {'task': 'about_update_price', 'schedule': crontab(0, 8, day_of_month=1)},
    {'task': 'irk.weather.tasks.openweathermap_current', 'schedule': crontab(0, '*/6')},
    {'task': 'irk.weather.tasks.openweathermap_detailed', 'schedule': crontab(0, '*/6')},
    {'task': 'weather_grabber_maps', 'schedule': crontab(0)},
    {'task': 'statistic_social_shares', 'schedule': crontab('*/30')},
    {'task': 'profiles_process_bounces', 'schedule': crontab(0, '*/6')},
    {'task': 'profiles_unban', 'schedule': crontab(0)},
    {'task': 'profiles_clean', 'schedule': crontab(20, 4, '*/2')},
    {'task': 'news_articles_paid_unset', 'schedule': crontab(0)},
    {'task': 'hitcounters_update_scroll_depth', 'schedule': crontab('2,12,22,32,42,52')},
    {'task': 'statistic_material_metrics', 'schedule': crontab('4,14,24,34,44,54')},
    {'task': 'hitcounters_by_day_update', 'schedule': crontab(0)},
    {'task': 'hitcounters_update_values', 'schedule': crontab('6,16,26,36,46,56')},
    {'task': 'adv.tasks.place_empty_notif', 'schedule': crontab(0, 7)},
    {'task': 'currency_grabber_exchange', 'schedule': crontab(15, '7,15')},
    {'task': 'adv_update_log', 'schedule': crontab(15, 4)},
    {'task': 'irk.adv.tasks.clickhouse_import', 'schedule': crontab('*/11')},
]

# Convert [{'task': 'name', 'schedule': 1},] to {'name':{'task': 'name', 'schedule': 1},}
BEAT_SCHEDULE = dict(zip([x['task'] for x in PERIODIC_TASKS], PERIODIC_TASKS))
