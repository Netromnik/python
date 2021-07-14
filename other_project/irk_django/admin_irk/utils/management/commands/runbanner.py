# -*- coding: utf-8 -*-
"""
Запуск баннерного сервера: `./manage.py runbanner`
"""
from __future__ import absolute_import, unicode_literals

import tornado.ioloop
from django.core.management.base import BaseCommand
from tornado.httpserver import HTTPServer
from tornado.netutil import bind_sockets

from servers.banner import Application


class Command(BaseCommand):
    help = "Запускает баннерный сервер для разработки"

    default_port = '8083'

    def add_arguments(self, parser):
        parser.add_argument(
            'addrport', nargs='?',
            help='Optional port number, or ipaddr:port'
        )
        parser.add_argument(
            '--nodebug', action='store_false', dest='debug_mode', default=True,
            help='Отключает отладочный режим',
        )

    def handle(self, *args, **options):

        if not options['addrport']:
            self.addr = '127.0.0.1'
            self.port = self.default_port
        else:
            self.addr, self.port = options['addrport'].split(':')

        self.debug = options['debug_mode']
        application = Application(debug=self.debug)

        sockets = bind_sockets(int(self.port), self.addr)  # port, ip
        server = HTTPServer(application, xheaders=True)
        server.add_sockets(sockets)
        server.start()

        self.stdout.write((
            "Starting banners server at http://%(addr)s:%(port)s/\n"
        ) % {
            "addr": self.addr,
            "port": self.port,
        })

        tornado.ioloop.IOLoop.instance().start()
