from django.contrib import admin
from .models import WikiArticleModel,WikiPermModel
# Register your models here.

# Wiki
@admin.register(WikiArticleModel)
class CustomGroupAdmin(admin.ModelAdmin):
    search_fields = ('title','level')

@admin.register(WikiPermModel)
class CustomGroupAdmin(admin.ModelAdmin):
    pass