# coding=utf-8

from __future__ import unicode_literals

import logging
import re

from django.core.management.base import BaseCommand
from irk.gallery.models import GalleryPicture
from irk.obed.models import Article

# манипуляции с stdout нужны, потому что обычный print не работает, если
# скрипт вызывать с редиректом вывода: ./manage.py news_migrate_obed_images > log.txt
stdout = None

IMAGE_BB = re.compile(r'\[\s*image\s+([,\d]+)(.*?)\]')

class Command(BaseCommand):
    help = 'Добавляет к картинкам в обеде параметр upscale, чтобы на фронте они растянулись'

    def handle(self, **options):
        global stdout
        stdout = self.stdout

        self.stdout.write('Start migrating obed images')

        query = Article.objects.filter(is_hidden=False).select_subclasses() \
            .filter(id__gte=38500) \
            .order_by('id')

        for article in query:
            self.stdout.write('#{} {} {}'.format(article.id, type(article), article.title))
            self.process_article(article)

        self.stdout.write('All images migrated')

    def process_article(self, article):
        new_content = replace_bb_codes(article.content)
        if new_content != article.content:
            article.content = new_content
            article.save(update_fields=['content'])
            self.stdout.write('   article saved')


def replace_bb_codes(content):
    return IMAGE_BB.sub(replace_callback, content)


def replace_callback(match):
    original_string = match.group(0)
    img, options = match.groups()[:2]

    # исправим ошибочно записанный тег images
    if ',' in img:
        return original_string.replace('image', 'images')

    # имиджи с параметрами оставляем как есть
    if options:
        return original_string

    if not is_upscale_required(img):
        return original_string

    new_string = '[image {} upscale]'.format(img)
    stdout.write('   replacing {} -> {}'.format(original_string, new_string))

    return new_string


def is_upscale_required(image_id):
    """
    Расширить ли это изображение до 805 пикс?

    Мы расширим только изображения шириной 620 пикселей, так как их подавляющее
    большинство.
    """
    try:
        picture = GalleryPicture.objects.get(id=image_id)
        width = picture.picture.image.width
    except GalleryPicture.DoesNotExist:
        stdout.write('  picture DoesNotExist {}'.format(image_id))
        return False
    except IOError:
        stdout.write('  file does not exist'.format(image_id))
        return False

    return width == 620


# pytest irk/news/management/commands/news_migrate_obed_images.py

def test_replace_bb_codes(monkeypatch):
    monkeypatch.setitem(globals(), "is_upscale_required", lambda x: True)

    assert replace_bb_codes('[image 1,2,3]') == '[images 1,2,3]'
    assert replace_bb_codes('[image 1]') == '[image 1 upscale]'
    assert replace_bb_codes('[image 1 upscale]') == '[image 1 upscale]'
    assert replace_bb_codes('[image 1 some options]') == '[image 1 some options]'
