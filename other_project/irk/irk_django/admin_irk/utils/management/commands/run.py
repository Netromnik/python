from django.core.management.commands.runserver import Command as RunServer

class Command(RunServer):
    """
    Ускоренный runserver.
    Отключены системные проверки django и проверки миграций
    """

    def check(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("SKIPPING SYSTEM CHECKS!\n"))

    def check_migrations(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("SKIPPING MIGRATION CHECKS!\n"))
