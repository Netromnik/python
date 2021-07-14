# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from irk.profiles.models import Profile
from irk.authentication.helpers import generate_identicon


class Command(BaseCommand):
    def handle(self, *args, **options):
        for profile in Profile.objects.filter(image=''):
            content = generate_identicon(profile.user_id)
            profile.image.save('identicon.png', ContentFile(content.getvalue()))
