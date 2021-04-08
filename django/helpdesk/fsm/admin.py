# users/admin.py
from django.contrib import admin
from .models import Queue,Task

def upper_case_name(obj):
    return ("%s %s" % (obj.first_name, obj.last_name)).upper()
upper_case_name.short_description = 'Name'

# Queue
# class StreamChoiceInline(admin.StackedInline):
#     model = Task
#     extra = 2
#     show_change_link =True
#     can_delete = False

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    model = Queue
    # inlines = [StreamChoiceInline,]
    search_fields = ('title',)

# Task
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass