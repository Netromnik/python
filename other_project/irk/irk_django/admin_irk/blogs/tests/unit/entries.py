# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django_dynamic_fixture import get
from django.core.urlresolvers import reverse

from irk.blogs.models import Author, UserBlogEntry

from irk.tests.unit_base import UnitTestBase
from irk.profiles.models import Profile


class BlogEntryTestCase(UnitTestBase):
    csrf_checks = False

    def test_create(self):
        author = get(Author, username='user', is_active=True, is_visible=True)
        get(Profile, user=author)
        title = self.random_string(10)
        caption = self.random_string(90)
        content = self.random_string(1000)
        url = reverse('news:blogs:create', args=(author.username,))

        # Проверяем, что отключенный автор не может писать посты
        author.is_operative = False
        author.save()
        self.assertEqual(404, self.app.get(url, status='*').status_code)

        author.is_operative = True
        author.save()

        form_vars = {'title': title,
                     'caption': caption,
                     'content': content,
                     'gallerypicture_set-TOTAL_FORMS': 48,
                     'gallerypicture_set-INITIAL_FORMS': 0,
                     'gallerypicture_set-MAX_NUM_FORMS': 48
                     }

        # Страница добавления поста
        response = self.app.get(url, form_vars, user=author)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/blogs/create.html')

        # Отправка формы
        response = self.app.post(url, form_vars, user=author).follow()

        self.assertContains(response, title)
        self.assertContains(response, content)
        url = response.context['entry'].get_absolute_url()

        # После добавления пост должен сразу быть виден
        response = self.app.get(url, user=None)
        self.assertContains(response, title)

    def test_update(self):
        author = get(Author, username='user', is_active=True, is_visible=True)
        get(Profile, user=author)
        post = get(UserBlogEntry, visible=True, author=author, last_comment=None)

        url = reverse('news:blogs:update', args=(author.username, post.id))

        # Проверяем, что отключенный автор не может писать посты
        author.is_operative = False
        author.save()
        self.assertEqual(404, self.app.get(url, status='*').status_code)

        author.is_operative = True
        author.save()

        response = self.app.get(url, user=None, status=403)
        self.assertEqual(response.status_code, 403)

        response = self.app.get(url, user=author)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/blogs/update.html')


class BlogsTestCase(UnitTestBase):
    """Страницы блогов"""

    def create_author(self):
        author = get(Author, username=self.random_string(5), is_active=True, is_visible=True)
        get(Profile, user=author)
        return author

    def test_index(self):
        """Индекс блогов"""

        # Создаем 5 авторов с постами
        authors = []
        for _ in range(0, 5):
            author = self.create_author()
            get(UserBlogEntry, visible=True, author=author, last_comment=None)
            authors.append(author)

        #  Одного автора скрываем
        authors[0].is_visible = False
        authors[0].save()

        # У другого скрываем единственный пост
        UserBlogEntry.objects.filter(author=authors[1]).update(visible=False)

        response = self.app.get(reverse('news:blogs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/blogs/index.html')
        self.assertEqual(len(response.context['objects']), 3)

    def test_authors(self):
        """Список авторов"""

        # Создаем 5 авторов с постами
        authors = []
        for _ in range(0, 5):
            author = self.create_author()
            get(UserBlogEntry, visible=True, author=author, last_comment=None, n=2)
            authors.append(author)

        #  Одного автора скрываем
        authors[0].is_visible = False
        authors[0].save()

        response = self.app.get(reverse('news:blogs:authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/blogs/authors.html')
        self.assertEqual(len(response.context['objects']), 4)

    def test_authors_posts(self):
        """Список постов автора"""

        author = self.create_author()
        get(UserBlogEntry, visible=True, author=author, last_comment=None, n=5)
        get(UserBlogEntry, visible=False, author=author, last_comment=None, n=2)

        url = reverse('newws:blogs:author', kwargs={"username": author.username, })
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/blogs/author.html')
        self.assertEqual(len(response.context['objects']), 5)  # Видны только открытые посты

        author.is_visible = False
        author.save()
        response = self.app.get(url, status='*')  # Никто не видит посты отключенного автора
        self.assertEqual(response.status_code, 404)

        response = self.app.get(url, status='*', user=author)  # Даже сам автор
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        """Пост в блоге"""

        author = self.create_author()
        post = get(UserBlogEntry, visible=True, author=author, last_comment=None)
        url = reverse('news:blogs:read', kwargs={"username": author.username, "entry_id": post.id})

        # Пост видим, и автор его виден
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/blogs/read.html')
        self.assertEqual(response.context['entry'], post)

        # Автор скрыт, а пост виден
        author.is_visible = False
        author.save()
        response = self.app.get(url, status='*')
        self.assertEqual(response.status_code, 404)

        # Автор виден, а пост скрыт
        author.is_visible = True
        author.save()
        post.visible = False
        post.save()
        response = self.app.get(url, status='*')
        self.assertEqual(response.status_code, 403)  # Никто пост не видит

        response = self.app.get(url, user=author)
        self.assertEqual(response.status_code, 200)  # А автор видит
        self.assertEqual(response.context['entry'], post)
