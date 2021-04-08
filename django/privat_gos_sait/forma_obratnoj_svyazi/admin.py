from django.contrib import admin
from .models import Contact_bd
# Register your models here.

class ConAdmin(admin.ModelAdmin):
    list_display=['name','email','phone','text','date']
    list_filter=['name']
    date_hierarchy = 'date'

admin.site.register(Contact_bd, ConAdmin)
