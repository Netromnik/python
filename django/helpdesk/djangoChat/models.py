from django.db import models
from django.contrib.auth import get_user_model
from fsm.models import Task
User = get_user_model()

class Message(models.Model):
	user = models.ForeignKey(User,on_delete=models.SET_NULL,blank=False,null=True,related_name="+")
	task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=False, null=True, related_name="taskchat")
	type = models.CharField(max_length=12)
	message = models.TextField(max_length=600)
	time = models.DateTimeField(auto_now_add=True)
	is_new = models.BooleanField(default=True)

	def __str__(self):
		return "".format(self.user,self.message)