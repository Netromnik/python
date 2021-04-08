from django.db import models

class ChatObjManager(models.Manager):
    def save_via_form(self,*args,**kwargs):
        #{'mesenge': 'asdas', 'status': 'O', 'change_user': <SimpleLazyObject: <CustomUser: fdsd dfg>>, 'task_id': 1}
        cls = {}
        cls['mesenge'] =    kwargs['mesenge']
        cls['change_user'] =kwargs['change_user']
        cls['task_id'] =    kwargs['task_id']
        self.create_messenge(**cls)

    def create_messenge(self, **kwargs):
        book = self.create(**kwargs)
        # do something with the book
        return book

    def get_chat(self,task):
        return self.filters(task=task).order_by('-created_at')
