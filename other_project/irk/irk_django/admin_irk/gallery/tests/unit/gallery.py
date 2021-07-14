# -*- coding: UTF-8 -*-
from __future__ import absolute_import
import json
import random
from irk.blogs.models import BlogEntry
from django.contrib.staticfiles.finders import find
from irk.gallery.models import GalleryPicture, Gallery, Picture
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G, F

from irk.news.models import Article
from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase


class GalleryTestCase(UnitTestBase):
    """Тесты вьюшек галереи"""

    csrf_checks = False

    def test_admin_multiupload(self):
        """Мультиаплоад в админе"""

        title = self.random_string(10)
        article = G(Article, title=title, source_site=Site.objects.get(slugs='news'), is_hidden=False)
        article_ct = ContentType.objects.get_for_model(Article)
        post_params = {
            'content_type_id': article_ct.id,
            'object_id': article.id,
        }
        files = [('Filedata', find('img/irkru.png')), ]

        self.assertEqual(Picture.objects.all().count(), 0)  # загруженных картинок нет
        response = self.app.post(reverse('gallery:admin_multiupload_handler'), post_params, upload_files=files)

        self.assertEqual(response.status_code, 200)
        data = json.loads(unicode(response.content))
        pictures = Picture.objects.all()
        self.assertEqual(pictures.count(), 1)
        self.assertEqual(data['picture'], pictures[0].id)

    def test_multiupload(self):
        """Мультиаплоад на клиенте"""

        blog = G(BlogEntry)
        blog_ct = ContentType.objects.get_for_model(BlogEntry)
        gallery = G(Gallery, object_id=blog.id, content_type=blog_ct)
        g_pic = G(GalleryPicture, id=random.randint(1, 20), gallery=gallery)
        post_params = {
            'content_type_id': blog_ct.id,
            'object_id': blog.id,
            'gallery_id': gallery.id,
            'id': g_pic.id,
        }
        files = [('Filedata', find('img/irkru.png')), ]

        response = self.app.post(reverse('gallery:multiupload_handler'), post_params, upload_files=files)

        self.assertEqual(response.status_code, 200)
        data = json.loads(unicode(response.content))
        self.assertEqual(data['gallerypicture'], g_pic.id)

    def test_delete_image(self):
        """Удалить изображение"""

        gallery = G(Gallery)
        picture = G(Picture)
        G(GalleryPicture, picture=picture, gallery=gallery)
        post_params = {
            'id': picture.id,
        }
        self.assertEqual(Picture.objects.all().count(), 1)

        response = self.app.post(reverse('gallery:delete_image'), post_params, user=self.create_user('vasya'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Picture.objects.all().count(), 0)

    def test_set_main_image(self):
        """Сделать изображение главным"""

        gallery = G(Gallery)
        picture = G(Picture)
        not_main = G(GalleryPicture, picture=picture, gallery=gallery)
        main = G(GalleryPicture, picture=G(Picture), gallery=gallery, main=True)
        get_params = {
            'id': picture.id,
        }

        response = self.app.get(reverse('gallery:main_image'), get_params, user=self.create_user('vasya'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(GalleryPicture.objects.get(id=not_main.id).main, True)
        self.assertEqual(GalleryPicture.objects.get(id=main.id).main, False)

    def test_set_best_image(self):
        """Сделать изображение лучшим"""

        gallery = G(Gallery)
        picture = G(Picture)
        not_best = G(GalleryPicture, picture=picture, gallery=gallery)
        best = G(GalleryPicture, picture=G(Picture), gallery=gallery, best=True)
        get_params = {
            'id': picture.id,
        }

        response = self.app.get(reverse('gallery:best_image'), get_params, user=self.create_user('vasya'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(GalleryPicture.objects.get(id=not_best.id).best, True)
        self.assertEqual(GalleryPicture.objects.get(id=best.id).best, False)

    def test_set_watermark(self):
        """Установить вотермарк на картинку"""

        gallery = G(Gallery)
        picture = G(Picture, watermark=False)
        G(GalleryPicture, picture=picture, gallery=gallery)
        params = {
            'id': picture.id,
        }
        user = self.create_user('vasya')

        response = self.app.post(reverse('gallery:set_watermark'), params, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Picture.objects.get(id=picture.id).watermark)

        response = self.app.post(reverse('gallery:set_watermark'), params, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Picture.objects.get(id=picture.id).watermark)

    def test_set_watermark_all(self):
        """Установить вотермарк для всех картинок галереи"""

        gallery = G(Gallery)
        G(GalleryPicture, picture=F(watermark=False), gallery=gallery, n=5)
        params = {
            'id': gallery.id,
            'check': 'true',
        }
        user = self.create_user('vasya')

        response = self.app.post(reverse('gallery:set_watermark_all'), params, user=user)
        self.assertEqual(response.status_code, 200)
        g_pics = GalleryPicture.objects.filter(gallery=gallery)
        for g_pic in g_pics:
            self.assertTrue(g_pic.picture.watermark)

        params['check'] = 'false'
        response = self.app.post(reverse('gallery:set_watermark_all'), params, user=user)
        self.assertEqual(response.status_code, 200)
        g_pics = GalleryPicture.objects.filter(gallery=gallery)
        for g_pic in g_pics:
            self.assertFalse(g_pic.picture.watermark)
