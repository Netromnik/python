# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase
from irk.news.models import Flash


class FlashNewsTestCase(UnitTestBase):
    """Тесты народных новостей"""

    csrf_checks = False

    def setUp(self):
        super(FlashNewsTestCase, self).setUp()
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.user = self.create_user('user')

    def test_index(self):
        """Индекс"""

        G(Flash, visible=True, n=5)
        G(Flash, visible=False, n=2)

        response = self.app.get(reverse('news:flash:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/flash/index.html')
        self.assertEqual(len(response.context['main_list']), 5)

        response = self.app.get(reverse('news:flash:index'), user=self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['main_list']), 7)

    def test_get_data(self):
        #TODO replace smoke-test
        """Получить список фоточек при загрузке новостей аяксом"""

        response = self.app.get(reverse('news:flash:data'))
        self.assertEqual(response.status_code, 200)

    def test_read(self):
        """Страница народной новости"""

        flash = G(Flash, title=self.random_string(20), visible=True)

        response = self.app.get(reverse('news:flash:read', args=(flash.id, )))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news-less/flash/read.html')
        self.assertEqual(response.context['entry'].title, flash.title)

    def test_toggle(self):
        """Удалить/восстановить новость"""

        G(Flash, visible=True, n=5)
        flash = G(Flash, title=self.random_string(20), visible=True)
        index_url = reverse('news:flash:index')
        page_url = reverse('news:flash:read', args=(flash.id, ))
        toggle_url = reverse('news:flash:toggle', args=(flash.id, ))

        # Попытка удаления обычным пользователем
        response = self.app.post(toggle_url, headers={'X_REQUESTED_WITH': 'XMLHttpRequest', },
                                 user=self.user, status='*')
        self.assertEqual(response.status_code, 403)

        # Удалили
        self.app.post(toggle_url, headers={'X_REQUESTED_WITH': 'XMLHttpRequest', }, user=self.admin)
        self.app.session.flush()

        response = self.app.get(index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['main_list']), 5)  # На одну меньше в списке

        response = self.app.get(page_url, status='*')  # Страница новости не открывается
        self.assertEqual(response.status_code, 404)

        # Восстановили
        self.app.post(toggle_url, headers={'X_REQUESTED_WITH': 'XMLHttpRequest', }, user=self.admin)
        self.app.session.flush()

        response = self.app.get(index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['main_list']), 6)

        response = self.app.get(page_url)
        self.assertEqual(response.status_code, 200)
