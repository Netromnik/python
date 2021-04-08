# users/admin.py
from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.auth.admin import UserAdmin, Group
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import *


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the resultes by users, content types and action flags
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)
    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"

@admin.register(LogHistory)
class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the resultes by users, content types and action flags
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
    ]


admin.site.unregister(Group)

def upper_case_name(obj):
    return ("%s %s" % (obj.first_name, obj.last_name)).upper()
upper_case_name.short_description = 'Name'

class FileChoiceInline(admin.StackedInline):
    model = File
    extra = 2
    show_change_link =True
    can_delete = False

# Queue
class StreamChoiceInline(admin.StackedInline):
    model = Stream
    extra = 2
    show_change_link =True
    can_delete = False

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    model = Queue
    inlines = [StreamChoiceInline,]
    search_fields = ('name',)


# CollectMedia
@admin.register(CollectMedia)
class CollectMediaAdmin(admin.ModelAdmin):
    inlines = [FileChoiceInline]
    search_fields = ('name',)
    ordering = ('name',)

# File
@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("__str__","collect","updated_at","created_at")
    # search_fields = ('name',)
    ordering = ('updated_at',)
    readonly_fields = ('document','created_at','updated_at')
    fields = [
        'document',
        'collect',
        'updated_at',
        'created_at'
    ]
    # fieldsets = [
    #     (None,               {'fields': ['document','collect']}),
    #     ('Date information', {'fields': ['updated_at',]}),
    # ]

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(CustomGroup)
class CustomGroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


# Task
class ChatChoiceInline(admin.StackedInline):
    model = ChatModel
    extra = 2
    show_change_link =True
    can_delete = False

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [ChatChoiceInline,]
    list_display = ("title","stream","status","updated_at","date_due")
    readonly_fields = ('created_at','updated_at')
    fieldsets = [
        ("Body task",{"fields":["title","description","file","status","date_due"]}),
        ("Req",{"fields":["stream","asignet_to",'chenge_user',"autors",]})
    ]
    search_fields = ["stream__description",]
