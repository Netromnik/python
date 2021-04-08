"""
Management utility to create superusers.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Used to create a superuser in cmd'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)
        parser.add_argument('password', nargs='+', type=str)

    def handle(self, *args, **options):
        obj = get_user_model()
        u=obj(username = options["username"][0])
        u.set_password(options["password"][0])
        u.is_active=True
        u.is_staff=True
        u.is_superuser=True
        u.save()
