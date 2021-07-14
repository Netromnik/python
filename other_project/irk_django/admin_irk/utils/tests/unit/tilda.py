# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tempfile
import zipfile

from django_dynamic_fixture import G

from irk.news.models import TildaArticle
from irk.tests.unit_base import UnitTestBase
from irk.utils.tilda import TildaArchive, IrkruTildaArchive


# запускать так:
# ./manage.py test irk.utils.tests.unit.tilda --keepdb

class MyTildaArchive(TildaArchive):
    def __init__(self, path):
        super(MyTildaArchive, self).__init__(path)
        self.processed_files = []
    def process_file(self, zf, zipinfo):
        with zf.open(zipinfo) as f:
            self.processed_files.append((zipinfo, f.read()))


class TildaArchiveTest(UnitTestBase):

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile()
        self.path = self.create_archive()

    def create_archive(self):
        with zipfile.ZipFile(self.tmpfile, 'w') as zf:
            zf.writestr('project999/css/tilda-blocks-2.12.css', b'content')
            zf.writestr('project999/css/tilda-grid-3.0.min.css', b'content')
            zf.writestr('/project999/js/bootstrap.min.js', b'content')
            zf.writestr('/project999/readme.txt', b'content')  # иногда со слешем

        return self.tmpfile.name

    def test_process_works(self):
        """Функция process_file вызывается для каждого файла"""
        archive = MyTildaArchive(self.path)
        archive.process()
        self.assertEqual(len(archive.processed_files), 4)
        self.assertEqual(archive.processed_files[1][1], b'content')

    def test_strip_project(self):
        self.assertEquals(TildaArchive.strip_project('project1/some.txt'), 'some.txt')
        self.assertEquals(TildaArchive.strip_project('/project11/some.txt'), 'some.txt')
        self.assertEquals(TildaArchive.strip_project('/project11/css/some.txt'), 'css/some.txt')
        self.assertEquals(TildaArchive.strip_project('/css/some.txt'), 'css/some.txt')

    def test_asset_detection(self):
        self.assertTrue(TildaArchive.is_css('css/hello.css'))
        self.assertTrue(TildaArchive.is_css('images/hello.css'))  # галерея зероблока кладет css в папку images
        self.assertTrue(TildaArchive.is_js('js/hello.js'))
        self.assertTrue(TildaArchive.is_js('images/hello.js'))  # галерея зероблока кладет js в папку images
        self.assertTrue(TildaArchive.is_image('images/tild6331-3631-4565-b738-663962636565__dsc03230.jpg'))
        self.assertTrue(TildaArchive.is_image('images/kprf.svg'))
        self.assertFalse(TildaArchive.is_js('rootkit.js'))

    def test_is_image(self):
        self.assertTrue(TildaArchive.is_image('images/hello.png'))
        self.assertFalse(TildaArchive.is_image('images/hello.png.exe'))
        self.assertFalse(TildaArchive.is_image('images/hello.png\nsome'))

    def test_extract(self):
        class MyMyTildaArchive(MyTildaArchive):
            def extract_path(self, zipinfo, f):
                return

        archive = MyTildaArchive(self.path)
        archive.process()


class IrkruTildaArchiveTest(UnitTestBase):

    def test_works(self):
        material = G(TildaArticle)
        archive = IrkruTildaArchive('/some/file', material)
        self.assertIsNotNone(archive)

    def test_assets(self):
        data = """
        <head>
            <link rel="stylesheet" href="css/tilda-grid-3.0.min.css" type="text/css" media="all" />
            <link rel='stylesheet' href='css/tilda-grid-3.0.min.css' type="text/css" media="all" />
            <link href="css/tilda-grid-3.0.min.css" rel='stylesheet' type="text/css" media="all" />
            <a href="css/tilda.css">
            <script src="js/some.js"></script>
            <script  src='js/some.js'></script>
            <script>alert('hello');
                </script> // да, тоже можно
        </head>
        <script src="js/some.js"></script>  // из контента не берем
        """
        styles, scripts = IrkruTildaArchive.find_assets(data)
        self.assertEqual(len(styles), 3)
        self.assertEqual(len(scripts), 3)

    def test_jquery_commented_out(self):
        """
        jquery сохраняется закомментированным, потому что конфликтует с нашим джейквери
        """

        archive = IrkruTildaArchive('/some/file', material=None)
        archive.scripts = ['<script src="js/jquery-1.10.2.min.js"></script>',
                           '<script src="js/jquery-migrate3.min.js"></script>']
        archive.comment_jquery()

        self.assertEqual(archive.scripts[0], '<!--<script src="js/jquery-1.10.2.min.js"></script>-->')
        self.assertEqual(archive.scripts[1], '<script src="js/jquery-migrate3.min.js"></script>')
