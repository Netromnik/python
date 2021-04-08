from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404
from django.test import TestCase, RequestFactory

from base.models import CustomUser, Task, Stream, Queue, CustomGroup
from view.dasbord import Dasbord
from view.s.kanban import KanbalDefault
from view.s.resolve import router
from view.s.table import Table
from view.ticket_crud.CreateTicket import ContactView
from view.ticket_crud.TicketView import DetailTask


class CustomTest(TestCase):
    #

    def setUp(self) -> None:
        ### add user case and groups
        self.user = CustomUser.objects.create_user(
            username= "test-user",
            password="123123",
        )
        self.user_an = CustomUser.objects.create_user(
            username= "test-user-an",
            password="123123",
        )
        self.user.save()
        self.group_for_user = CustomGroup.obj.create(name="test-groups-via-user"); self.group_for_user.save()
        self.group_not_for_user = CustomGroup.obj.create(name="test-groups-not-via-user"); self.group_not_for_user.save()
        self.user.groups.add(self.group_for_user)
        self.user.save()
        self.rf = RequestFactory()

        self.q = Queue.obj.create(name="test-q"); self.q.save()
        self.nq = Queue.obj.create(name="test-nq"); self.nq.save()
        self.stream_u =  Stream.obj.create  ( description="",queue = self.q )
        self.stream =  Stream.obj.create    (   description="",queue = self.nq )

    #         /
    def test_path_perm_dasbord(self):
        reques = self.rf.get("/")
        # test sacefull perm
        # autch user is 200
        reques.user = self.user
        response = Dasbord.as_view()(reques)
        self.assertEqual(response.status_code,200)
        # anon user is 302 redirect
        reques.user = AnonymousUser()
        response = Dasbord.as_view()(reques)
        self.assertEqual(response.status_code,302)

    # /<int:slug_query_pk>/<int:slug_stream_pk>/
    def test_path_perm_route(self):
        reques = self.rf.get("")
        # test sacefull perm
        # autch user is 200
        reques.user = self.user
        self.assertIsInstance(self.q.pk,int)
        response = router(reques,slug_query_pk = int(self.q.pk),slug_stream_pk=int(self.stream_u.pk))
        # redirect user for setting view default
        self.assertEqual(response.status_code, 302)
        reques.user = AnonymousUser()
        response = router(reques,slug_query_pk = int(self.q.pk),slug_stream_pk=int(self.stream_u.pk))
        # if user not autch perm raise
        self.assertEqual(response.status_code, 405)

    # /<int:slug_query_pk>/<int:slug_stream_pk>/kanban/
    def test_path_perm_kanbal(self):
        reques = self.rf.get("")
        # test sacefull perm
        # autch user is 200
        reques.user = self.user
        self.assertIsInstance(self.q.pk,int)
        response = KanbalDefault.as_view()(reques,slug_query_pk = int(self.q.pk),slug_stream_pk=int(self.stream_u.pk))
        self.assertEqual(response.status_code, 200)
        # if q not hav stream
        try:
            response = KanbalDefault.as_view()(reques, slug_query_pk=self.q.pk, slug_stream_pk=self.stream.pk)
        except Http404:
            # raise Http404 if q not hav stream
            self.assertEqual(response.status_code, 200)

        ## test if user Anon
        reques.user = AnonymousUser()
        self.assertIsInstance(self.q.pk,int)
        response = KanbalDefault.as_view()(reques,slug_query_pk = int(self.q.pk),slug_stream_pk=int(self.stream_u.pk))
        self.assertEqual(response.status_code, 302)
        # if q not hav stream
        try:
            response = KanbalDefault.as_view()(reques, slug_query_pk=self.q.pk, slug_stream_pk=self.stream.pk)
        except Http404:
            # raise Http404 if q not hav stream
            self.assertEqual(response.status_code, 302)

    # /<int:slug_query_pk>/<int:slug_stream_pk>/table/
    def test_path_perm_table(self):
        reques = self.rf.get("")
        # test sacefull perm
        # autch user is 200
        reques.user = self.user
        self.assertIsInstance(self.q.pk,int)
        response = Table.as_view()(reques,slug_query_pk = int(self.q.pk),slug_stream_pk=int(self.stream_u.pk))
        self.assertEqual(response.status_code, 200)
        # anon user is 302 redirect
        try:
            response = Table.as_view()(reques, slug_query_pk=self.q.pk, slug_stream_pk=self.stream.pk)
        except Http404:
            # raise Http404 if q not hav stream
            self.assertEqual(response.status_code, 200)

        ## test if user Anon
        reques.user = AnonymousUser()
        self.assertIsInstance(self.q.pk,int)
        response = KanbalDefault.as_view()(reques,slug_query_pk = int(self.q.pk),slug_stream_pk=int(self.stream_u.pk))
        self.assertEqual(response.status_code, 302)
        # if q not hav stream
        try:
            response = KanbalDefault.as_view()(reques, slug_query_pk=self.q.pk, slug_stream_pk=self.stream.pk)
        except Http404:
            # raise Http404 if q not hav stream
            self.assertEqual(response.status_code, 302 )

    # /newticket/
    def test_path_perm_newticket(self):
        reques = self.rf.get("")
        # test sacefull perm
        # autch user is 200
        reques.user = self.user
        response = ContactView.as_view()(reques)
        self.assertEqual(response.status_code, 200)
        # test if user Anon
        reques.user = AnonymousUser()
        response = ContactView.as_view()(reques)
        self.assertEqual(response.status_code, 302)

    # /ticket/<int:pk>/
    def test_path_perm_ticket_view(self):
        reques = self.rf.get("")
        # test sacefull perm
        # autch user is 200
        kwargs = {  }
        task_authors = Task.obj.create(
                                       title="test-task-au",
                                       description="test-d",
                                       status='W',
                                       stream=self.stream_u,
                                       autors = self.user,
                                       )
        task_assigned = Task.obj.create(
                                       title="test-task-as",
                                       description="test-d",
                                       status='W',
                                       stream=self.stream_u,
                                       asignet_to = self.user,
                                       autors = self.user_an,
                                       )
        task_not_assigned = Task.obj.create(
                                       title="test-task-nas",
                                       description="test-d",
                                       status='W',
                                       stream=self.stream_u,
                                       asignet_to = None,
                                       autors = self.user_an,
                                       )
        reques.user = self.user
        # View is avtor
        response = DetailTask.as_view()(reques,pk=task_authors.pk)
        self.assertEqual(response.status_code, 200)
        # View is assigned
        response = DetailTask.as_view()(reques,pk=task_assigned.pk)
        self.assertEqual(response.status_code, 200)
        # view is not assigned
        response = DetailTask.as_view()(reques,pk=task_not_assigned.pk)
        self.assertEqual(response.status_code, 200)
        # test if user Anon
        reques.user = AnonymousUser()
        response = DetailTask.as_view()(reques,pk=task_authors.pk)
        self.assertEqual(response.status_code, 302)
        response = DetailTask.as_view()(reques,pk=task_assigned.pk)
        self.assertEqual(response.status_code, 302)
        response = DetailTask.as_view()(reques,pk=task_not_assigned.pk)
        self.assertEqual(response.status_code, 302)

    # /updateticket/<int:pk>/
    # def test_path_perm_update_ticket(self):
        # reques = self.rf.get("")
        # # autch user is 200
        # kwargs = {  }
        # task_authors = Task.obj.create(
        #                                title="test-task-au",
        #                                description="test-d",
        #                                status='W',
        #                                stream=self.stream_u,
        #                                autors = self.user,
        #                                )
        # task_assigned = Task.obj.create(
        #                                title="test-task-as",
        #                                description="test-d",
        #                                status='W',
        #                                stream=self.stream_u,
        #                                asignet_to = self.user,
        #                                autors = self.user_an,
        #                                )
        # task_not_assigned = Task.obj.create(
        #                                title="test-task-nas",
        #                                description="test-d",
        #                                status='W',
        #                                stream=self.stream_u,
        #                                asignet_to = None,
        #                                autors = self.user_an,
        #                                )
        # reques.user = self.user
        # # View is avtor
        # response = UpdateView.as_view()(reques,pk=task_authors.pk)
        # self.assertEqual(response.status_code, 200)
        # # View is assigned
        # response = UpdateView.as_view()(reques,pk=task_assigned.pk)
        # self.assertEqual(response.status_code, 200)
        # # view is not assigned
        # response = UpdateView.as_view()(reques,pk=task_not_assigned.pk)
        # self.assertEqual(response.status_code, 200)
        # # test if user Anon
        # reques.user = AnonymousUser()
        # response = UpdateView.as_view()(reques,pk=task_authors.pk)
        # self.assertEqual(response.status_code, 302)
        # response = UpdateView.as_view()(reques,pk=task_assigned.pk)
        # self.assertEqual(response.status_code, 302)
        # response = UpdateView.as_view()(reques,pk=task_not_assigned.pk)
        # self.assertEqual(response.status_code, 302)
