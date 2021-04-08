from django.contrib import admin
from .models import name_cat,items_cat
from django.db import models
from mdeditor.widgets import MDEditorWidget
# Register your models here.
@admin.register(name_cat)
class Name_admin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('name',)}

@admin.register(items_cat)
class Items_index(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}
    list_display=['name','categoy']
    formfield_overrides = {
        models.TextField:{'widget':MDEditorWidget}
    }
