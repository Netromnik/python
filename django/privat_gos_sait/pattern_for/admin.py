from django.contrib import admin
from .models import pattern_for #,categoy
from django.db import models

from mdeditor.widgets import MDEditorWidget
#
# class CatAdmin(admin.ModelAdmin):
#     list_display=['name','slug']
#     prepopulated_fields={'slug':('name',)}

class Prod_Admin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'categoy', 'price']
    fieldsets=(
            ('Items',{
                'fields':('name','slug','categoy','image_title')}),
            ('POST',{'fields':('image_priview','text','price')})
            )
    prepopulated_fields = {'slug': ('name',)}
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }    
# admin.site.register(categoy,CatAdmin)

admin.site.register(pattern_for,Prod_Admin)

