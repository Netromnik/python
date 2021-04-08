from django.test import TestCase
from django.contrib.auth.models import User,Group
from django.test.client import RequestFactory
from .models import Queue,Task,STATES_list
from django.core.exceptions import ObjectDoesNotExist
from django_fsm import has_transition_perm
from .stat_logick import dispath

# Create your tests here.
class TaskTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username= "test-user",
            password="123123",
        )
        self.user_an = User.objects.create_user(
            username= "test-user-an",
            password="123123",
        )
        self.user.save()
        self.group_for_user = Group.objects.create(name="test-groups-via-user"); self.group_for_user.save()
        self.group_not_for_user = Group.objects.create(name="test-groups-not-via-user"); self.group_not_for_user.save()
        self.user.groups.add(self.group_for_user)
        self.user.save()

    def test_create(self):
        rock = Queue.objects.create(title="Rock")
        blues = Queue.objects.create(title="Blues")
        Queue.objects.create(title="Hard Rock", parent=rock)
        Queue.objects.create(title="Pop Rock", parent=rock)

    def test_save_task(self):
        rock = Queue.objects.create(title="Rock")
        blues = Queue.objects.create(title="Blues")
        t1 = Queue.objects.create(title="Hard Rock", parent=rock)
        Queue.objects.create(title="Pop Rock", parent=rock)

        task = Task()
        task.title = "first"
        task.description = "I hate you"
        task.queue = rock
        task.owner = self.user
        task.save()
        task.queue = t1
        task.save()

    def test_state_1(self):
        rock = Queue.objects.create(title="Rock")
        task = Task()
        task.title = "first"
        task.description = "I hate you"
        task.queue = rock
        task.owner = self.user
        task.save()

        if not has_transition_perm(task.start,self.user):
            task.start(self.user)

    def test_task_stat(self):
        v1 = dispath(stat=STATES_list[0],type='owner')
        v2 = dispath(stat=STATES_list[0],type='responsible')
        [ dispath(stat=i,type='owner')  for i in  STATES_list]
        [ dispath(stat=i,type='responsible')  for i in  STATES_list]
        dispath(stat="HZS",type='owner')
        self.assertIsNone(dispath(stat=STATES_list[0],type="FAST"),msg="Is field type stat_logick dead")


    # def test_history(self):
    #     rock = Queue.objects.create(title="History-test")
    #     task = Task()
    #     task.title = "first"
    #     task.description = "I hate you"
    #     task.queue = rock
    #     task.owner = self.user
    #     task.save()
    #     alert(task,"this messege")
    #     l = get_list(user=self.user)
    #     assert len(l) == 1 ,"onli active alert"
    #     l = get_list(user=self.user,all_q=True)
    #     assert len(l) == 1 ,"all alert"
    #     l = get_list(user=self.user)
    #     assert len(l) == 0 ,"not allert"

