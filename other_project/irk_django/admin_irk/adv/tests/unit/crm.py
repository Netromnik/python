# -*- coding: UTF-8 -*-
from irk.adv.models import Client, MailHistory
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G
from irk.tests.unit_base import UnitTestBase


class TestCRM(UnitTestBase):
    """Вьюхи для CRM"""

    def setUp(self):
        super(TestCRM, self).setUp()
        self.user = self.create_user('user', 'user', is_admin=True)

    def test_booking(self):
        """Страница бронирования"""
        # TODO: replace smoke test

        url = reverse('adv_crm:crm.index')
        self.assertIsOpening(url, self.user)

    def test_clients_list(self):
        """Страница списка клиентов"""
        # TODO: replace smoke test

        url = reverse('adv_crm:clients.clientsList')
        self.assertIsOpening(url, self.user)

    def test_client_read(self):
        """Страница клиента"""
        # TODO: replace smoke test

        client = G(Client)
        url = reverse('adv_crm:clients.clientRead', kwargs={'client_id': client.id})
        self.assertIsOpening(url, self.user)

    def test_reports(self):
        """Страница для генерации отчетов"""
        # TODO: replace smoke test

        url = reverse('adv_crm:crm_reports.reports')
        self.assertIsOpening(url, self.user)

    def test_mail_read(self):
        """Страница письма из рассылки"""
        # TODO: replace smoke test

        message = G(MailHistory)
        url = reverse('adv_crm:mail.mailRead', kwargs={'message_id': message.id})
        self.assertIsOpening(url, self.user)

    def test_preview_message(self):
        """Превью шаблона письма"""
        # TODO: replace smoke test

        url = reverse('adv_crm:mail.previewMessage')
        self.assertIsOpening(url, self.user)

    def test_duties(self):
        """Страница дел на сегодня"""
        # TODO: replace smoke test

        url = reverse('adv_crm:communications.duties')
        self.assertIsOpening(url, self.user)
