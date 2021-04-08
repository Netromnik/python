from  django.test import TestCase ,Client
from  base.models import CustomUser, Task,Stream,Queue,CustomGroup
from django.conf import settings

class CustomTest(TestCase):
    client_anon = Client()
    client_deanon = Client()
    user = None
    def _create_support(self):
        pass
        # gr = CustomGroup(name="test") ; gr.save()
        # self.user.groups.add(gr)
        # q =Queue(name="Qtest",groups=gr) ; q.save()
        # stream = Stream(description="Stest",queue=q)
        # self._creatTask(stream,"test",self.user,Task.STATUS[0][0])

    def _creatTask(self,s,title,user,status):
        t = Task()
        t.title = title
        t.description = 'description'
        t.stream = s
        t.autors = user
        t.status = status
        t.save()
        return t

    def _creatS(self,gr_name,q_name,s_name,t_name,user):
        gr = CustomGroup.obj.get_or_create(name=gr_name) ; gr.save()
        q =Queue.obj.get_or_create(name=q_name,groups=gr) ; q.save()
        stream = Stream.obj.get_or_create(description=s_name,queue=q)
        task =self._creatTask(stream,t_name,user,Task.STATUS[0][0])
        return [gr,q,stream,task]

    @classmethod
    def setUpTestData(self):
        self.user = CustomUser.objects.create_user(username='testU')
        self.user.set_password("testpass")
        self.user.save()

        flag = self.client_deanon.force_login(self.user)
        if flag == False:
            raise
        super(CustomTest, self).__init__()


    def test_autch(self):
        respons = self.client_anon.get("/")
        status_redirect = 302
        self.assertEqual(respons.status_code,status_redirect)
        self.assertEqual(respons.path,settings.LOGIN_URL)
        self.client_deanon.get("/")
        status_ok = 200
        self.assertEqual(respons.status_code, status_ok)
        self.assertEqual(respons.path, "/")


class DasbordTest(CustomTest):
    # create 3 set
    #           -1 set autor
    #           -2 set unsignet
    #           -3 set user signet


    def test_TableSet(self):
        l = self._creatS(gr_name="test",q_name="f",s_name="ff",t_name="test0",user=self.user)
        autor = self.user.get_autor_q()
        self.assertEqual(autor[0],l[-1])
        u = CustomUser.objects.create_user(username="UtestO",password="test")

        l = self._creatS(gr_name="test2",q_name="fff",s_name="ffff",t_name="test1",user=u)
        unsignet =self.user.get_unsignet_q()
        self.assertEqual(unsignet[0],l[-1])

        l[-1].asignet_to = self.user
        signet =self.user.get_signet_q()
        self.assertEqual(signet[0], l[-1])

    def test_append(self):
        u = CustomUser.objects.create_user(username="Utest1",password="test")
        l = self._creatS(gr_name="test2", q_name="fff", s_name="ffff", t_name="test2", user=u)

        respons = self.client_anon.get("/",data={'pk': l[-1].pk})
        status_redirect = 302
        self.assertEqual(respons.status_code,status_redirect)
        self.assertEqual(respons.path,settings.LOGIN_URL)

        self.client_deanon.get("/",data={'pk': l[-1].pk})
        self.assertEqual(l[-1].asignet_to, self.user)