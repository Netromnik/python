from django.contrib import admin
# from django.contrib.admin.sites import DefaultAdminSite
from django.contrib.auth.models import User, Group
# from django.utils.translation import ugettext_lazy

admin.site.unregister(User)
admin.site.unregister(Group)
