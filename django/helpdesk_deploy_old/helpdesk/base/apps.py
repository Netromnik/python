from django.apps import AppConfig

class BaseConfig(AppConfig):
    name = 'base'
    verbose_name = "Система заявок"

    def ready(self):
        import base.alert_signals    # noqa

