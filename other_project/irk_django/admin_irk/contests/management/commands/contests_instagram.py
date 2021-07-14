# -*- coding: utf-8 -*-

import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from irk.contests.models import Contest, Participant
from irk.gallery.models import Gallery, GalleryPicture, Picture
from irk.utils.grabber.instagram import load_media_by_hashtag



class Command(BaseCommand):
    """Обновление фотографий по всем открытым instagram-конкурсам"""

    def handle(self, *args, **options):
        contests = Contest.objects.filter(type=Contest.TYPE_INSTAGRAM,
                                          date_end__gte=datetime.date.today()).exclude(instagram_tag='')

        for contest in contests:
            try:
                latest_photo_id = Participant.objects.filter(contest=contest).order_by('-id')\
                    .values_list('instagram_id', flat=True)
            except IndexError:
                latest_photo_id = None

            for photo in load_media_by_hashtag(contest.instagram_tag, latest_photo_id=latest_photo_id,
                                               text_truncate_size=255):  # Длина `Participant.title`

                if Participant.objects.filter(contest=contest, instagram_id=photo['id']).exists():
                    continue

                participant = Participant(contest=contest, title=photo['title'], username=photo['username'],
                                          instagram_id=photo['id'])
                participant.save()

                content_type = ContentType.objects.get_for_model(Participant)
                try:
                    gallery = participant.gallery.all()[0]
                except IndexError:
                    gallery = Gallery.objects.create(content_type=content_type, object_id=participant.id)

                picture = Picture(title=photo['title'], watermark=False)
                picture.save()
                file_ = ContentFile(photo['image']['content'])
                picture.image.save(photo['image']['name'], file_)

                gp = GalleryPicture(picture=picture, gallery=gallery, main=True)
                gp.save()
