from django.contrib import admin
from .models import Post ,categor_post
from markdownx.admin import MarkdownxModelAdmin
from markdownx.widgets import AdminMarkdownxWidget

class Postadm(admin.ModelAdmin):
    formfield_overrides = {
        Post.content: {'widget': AdminMarkdownxWidget},
    }


class Catadm(admin.ModelAdmin):
    pass
admin.site.register(Post,MarkdownxModelAdmin)
admin.site.register(categor_post,Catadm)
